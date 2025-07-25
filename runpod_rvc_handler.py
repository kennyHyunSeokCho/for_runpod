import runpod
import subprocess
import os

def run_gpu_synthesis(input_data):
    """
    실제로 all_in.py를 subprocess로 실행 (최대 3시간 대기)
    input_data에서 필요한 인자를 추출해 all_in.py에 넘길 수 있음
    """
    try:
        # 예시: 인자가 필요하면 아래처럼 input_data에서 꺼내서 추가
        # arg1 = input_data.get('user_vocal_url', '')
        # arg2 = input_data.get('vocal_file_url', '')
        # arg3 = input_data.get('mr_file_url', '')
        # args = ["python3", "all_in.py", arg1, arg2, arg3]
        args = ["python3", "all_in.py"]  # 인자 필요시 위처럼 추가
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=10800  # 최대 3시간(초)
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "message": "all_in.py 실행 완료" if result.returncode == 0 else "all_in.py 실행 실패",
            # 필요시 실제 S3 URL 등 추가
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": "all_in.py 실행이 3시간을 초과하여 강제 종료됨.",
            "message": "all_in.py 실행 타임아웃"
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "message": "all_in.py 실행 중 예외 발생"
        }

def handler(event):
    input_data = event.get("input", {})
    print(f"받은 input 데이터: {input_data}")
    result = run_gpu_synthesis(input_data)
    return result

runpod.serverless.start({"handler": handler}) 
