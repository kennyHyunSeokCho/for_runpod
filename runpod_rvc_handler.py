import runpod
import boto3
import os
import json
import tempfile

# S3 설정값을 하드코딩 (개인 프로젝트용)
AWS_ACCESS_KEY = 'AKIARBG23HMO2PBHIWYK'
AWS_SECRET_KEY = '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'
REGION_NAME = 'ap-northeast-2'
BUCKET_NAME = 'ai-vocal-training'

# S3 클라이언트 생성 함수 (하드코딩 값 사용)
def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=REGION_NAME
    )

# S3에서 파일 다운로드
def download_from_s3(s3_client, bucket_name, s3_key, local_path=None):
    import tempfile
    try:
        if local_path is None:
            temp_dir = tempfile.mkdtemp()
            file_name = os.path.basename(s3_key)
            local_path = os.path.join(temp_dir, file_name)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        s3_client.download_file(bucket_name, s3_key, local_path)
        return local_path
    except Exception as e:
        print(f"S3 다운로드 실패: {str(e)}")
        return None

# S3에 파일 업로드
def upload_file_to_s3(s3_client, local_file_path, bucket_name, s3_key):
    try:
        s3_client.upload_file(local_file_path, bucket_name, s3_key)
        print(f"S3 업로드 완료: {local_file_path} → s3://{bucket_name}/{s3_key}")
        return True
    except Exception as e:
        print(f"S3 업로드 실패: {e}")
        return False


def handler(event):
    # 1. input 전체를 그대로 추출
    input_data = event.get("input", {})

    # 2. (예시) input_data를 임시 JSON 파일로 저장 (subprocess 등에서 활용 가능)
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        json.dump(input_data, f, ensure_ascii=False)
        input_json_path = f.name

    # 3. S3 클라이언트 준비 (하드코딩 값 기반)
    s3_client = get_s3_client()
    if s3_client is None:
        return {"success": False, "message": "S3 클라이언트 초기화 실패"}

    # 4. user_vocal_url, singer_embedding_url 등 S3에서 다운로드 (필요시)
    user_vocal_url = input_data.get("user_vocal_url")
    singer_embedding_url = input_data.get("singer_embedding_url")
    local_vocal = download_from_s3(s3_client, BUCKET_NAME, user_vocal_url) if user_vocal_url else None
    local_embedding = download_from_s3(s3_client, BUCKET_NAME, singer_embedding_url) if singer_embedding_url else None
    if user_vocal_url and not local_vocal:
        return {"success": False, "message": "user_vocal_url 다운로드 실패"}
    if singer_embedding_url and not local_embedding:
        return {"success": False, "message": "singer_embedding_url 다운로드 실패"}

    # 5. RVC 추론 실행 (input_data 전체를 그대로 전달)
    # 실제로는 run_rvc_inference(input_data) 또는 subprocess로 실행
    # 여기서는 예시로 단순 복사
    output_path = local_vocal.replace(".wav", "_synth.wav") if local_vocal else "output_synth.wav"
    import shutil
    if local_vocal:
        shutil.copy(local_vocal, output_path)
    else:
        # 입력 파일 없으면 빈 파일 생성 (테스트용)
        with open(output_path, "wb") as f:
            f.write(b"")

    # 6. 결과 파일 S3 업로드
    output_s3_key = f"output/{os.path.basename(output_path)}"
    upload_success = upload_file_to_s3(s3_client, output_path, BUCKET_NAME, output_s3_key)
    if not upload_success:
        return {"success": False, "message": "결과 파일 S3 업로드 실패"}

    # 7. 결과 URL 생성
    output_url = f"https://{BUCKET_NAME}.s3.{REGION_NAME}.amazonaws.com/{output_s3_key}"

    return {
        "success": True,
        "output_url": output_url,
        "message": "합성 완료"
    }

runpod.serverless.start({"handler": handler}) 
