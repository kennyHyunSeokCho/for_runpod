import runpod
import subprocess
import os

def run_gpu_synthesis(input_data):
    """
    /workspace/test_model.py를 subprocess로 실행 (최대 3시간 대기)
    input_data에서 필요한 인자를 추출해 test_model.py에 넘깁니다.
    디버깅을 위해 작업 디렉토리, 파일 목록, 실행 명령어, 인자값을 모두 출력합니다.
    """
    try:
        # input_data에서 인자 추출 (test_model.py 인자와 완전히 일치)
        user_id = input_data.get('user_id', '')
        artist = input_data.get('artist', '')
        title = input_data.get('title', '')
        user_vocal_s3 = input_data.get('user_vocal_s3', '')
        vocal_s3 = input_data.get('vocal_s3', '')
        inst_s3 = input_data.get('inst_s3', '')
        print(f"[DEBUG] user_id: {user_id}")
        print(f"[DEBUG] artist: {artist}")
        print(f"[DEBUG] title: {title}")
        print(f"[DEBUG] user_vocal_s3: {user_vocal_s3}")
        print(f"[DEBUG] vocal_s3: {vocal_s3}")
        print(f"[DEBUG] inst_s3: {inst_s3}")

        # 디버깅: 현재 작업 디렉토리와 파일 목록 출력
        print(f"[DEBUG] 현재 작업 디렉토리: {os.getcwd()}")
        print("[DEBUG] 현재 디렉토리 파일 목록:")
        for f in os.listdir('.'):
            print(f"  - {f}")
        print("[DEBUG] /workspace 디렉토리 파일 목록:")
        if os.path.exists('/workspace'):
            for f in os.listdir('/workspace'):
                print(f"  - /workspace/{f}")
        else:
            print("  (/workspace 디렉토리 없음)")

        # test_model.py의 절대경로 지정
        script_path = "/workspace/test_model.py"
        args = [
            "python3", script_path,
            "--user_id", user_id,
            "--artist", artist,
            "--title", title,
            "--user_vocal_s3", user_vocal_s3,
            "--vocal_s3", vocal_s3,
            "--inst_s3", inst_s3
        ]
        print(f"[DEBUG] 실행 명령어: {' '.join(args)}")
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=10800  # 최대 3시간(초)
        )
        print(f"[DEBUG] subprocess stdout:\n{result.stdout}")
        print(f"[DEBUG] subprocess stderr:\n{result.stderr}")
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "message": "test_model.py 실행 완료" if result.returncode == 0 else "test_model.py 실행 실패",
        }
    except subprocess.TimeoutExpired:
        print(f"[DEBUG] TimeoutExpired: test_model.py 실행이 3시간을 초과하여 강제 종료됨.")
        return {
            "success": False,
            "output": "",
            "error": "test_model.py 실행이 3시간을 초과하여 강제 종료됨.",
            "message": "test_model.py 실행 타임아웃"
        }
    except Exception as e:
        print(f"[DEBUG] 예외 발생: {e}")
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "message": "test_model.py 실행 중 예외 발생"
        }

def handler(event):
    input_data = event.get("input", {})
    print(f"받은 input 데이터: {input_data}")
    result = run_gpu_synthesis(input_data)
    return result

runpod.serverless.start({"handler": handler}) 
