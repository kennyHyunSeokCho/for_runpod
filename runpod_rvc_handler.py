import runpod
import os
import json
import tempfile
from vocal.s3_utils import get_s3_client_from_env, download_from_s3, upload_file_to_s3
# 실제 RVC 추론 함수는 아래에서 import 하거나 subprocess로 실행할 수 있습니다.
# from vocal.ai_synthesis_api import run_rvc_inference

def handler(event):
    # 1. input 전체를 그대로 추출
    input_data = event.get("input", {})

    # 2. (예시) input_data를 임시 JSON 파일로 저장 (subprocess 등에서 활용 가능)
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        json.dump(input_data, f, ensure_ascii=False)
        input_json_path = f.name

    # 3. S3 클라이언트 준비 (환경변수 기반)
    bucket_name = os.getenv("S3_BUCKET_NAME")
    s3_client = get_s3_client_from_env(bucket_name)
    if s3_client is None:
        return {"success": False, "message": "S3 클라이언트 초기화 실패"}

    # 4. user_vocal_url, singer_embedding_url 등 S3에서 다운로드 (필요시)
    user_vocal_url = input_data.get("user_vocal_url")
    singer_embedding_url = input_data.get("singer_embedding_url")
    local_vocal = download_from_s3(s3_client, bucket_name, user_vocal_url) if user_vocal_url else None
    local_embedding = download_from_s3(s3_client, bucket_name, singer_embedding_url) if singer_embedding_url else None
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
    upload_success = upload_file_to_s3(s3_client, output_path, bucket_name, output_s3_key)
    if not upload_success:
        return {"success": False, "message": "결과 파일 S3 업로드 실패"}

    # 7. 결과 URL 생성
    region = os.getenv("AWS_REGION", "ap-northeast-2")
    output_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{output_s3_key}"

    return {
        "success": True,
        "output_url": output_url,
        "message": "합성 완료"
    }

runpod.serverless.start({"handler": handler}) 