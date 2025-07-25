import runpod
import subprocess
import os

def run_gpu_synthesis(input_data):
    """
    실제로 all_in.py를 subprocess로 실행 (최대 3시간 대기)
    input_data에서 필요한 인자를 추출해 all_in.py에 넘길 수 있음
    """
    try:
        # 현재 디렉토리와 파일 목록 확인
        print(f"현재 작업 디렉토리: {os.getcwd()}")
        print("현재 디렉토리 파일 목록:")
        subprocess.run(["ls", "-la"], capture_output=False)
        
        # all_in.py 파일 찾기
        print("\nall_in.py 파일 찾기:")
        subprocess.run(["find", ".", "-name", "all_in.py"], capture_output=False)
        
        # 파일이 존재하는지 확인
        if os.path.exists("all_in.py"):
            print("all_in.py 파일이 현재 디렉토리에 있습니다.")
            script_path = "all_in.py"
        elif os.path.exists("/app/all_in.py"):
            print("all_in.py 파일이 /app 디렉토리에 있습니다.")
            script_path = "/app/all_in.py"
        else:
            print("all_in.py 파일을 찾을 수 없습니다!")
            return {
                "success": False,
                "output": "",
                "error": "all_in.py 파일을 찾을 수 없습니다.",
                "message": "파일 경로 오류"
            }
        
        # 예시: 인자가 필요하면 아래처럼 input_data에서 꺼내서 추가
        # arg1 = input_data.get('user_vocal_url', '')
        # arg2 = input_data.get('vocal_file_url', '')
        # arg3 = input_data.get('mr_file_url', '')
        # args = ["python3", script_path, arg1, arg2, arg3]
        args = ["python3", script_path]  # 인자 필요시 위처럼 추가
        
        print(f"실행할 명령어: {' '.join(args)}")
        
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
