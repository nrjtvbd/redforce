import zipfile
import os
import shutil
import subprocess
import sys

# কনফিগারেশন
zip_filename = 'redforce_main.zip'
extract_folder = 'temp_work'
zip_password = os.getenv("ZIP_PASS")

def main():
    if not zip_password:
        print("❌ Error: ZIP_PASS environment variable is not set in GitHub Secrets.")
        return

    if os.path.exists(extract_folder):
        shutil.rmtree(extract_folder)

    try:
        # জিপ ফাইল আনজিপ করা
        with zipfile.ZipFile(zip_filename, 'r') as zf:
            zf.extractall(path=extract_folder, pwd=zip_password.encode('utf-8'))
            print("✅ Successfully decrypted and extracted files.")

        # জিপের ভেতর থেকে update_redforce.py রান করা
        script_path = os.path.join(extract_folder, "update_redforce.py")
        
        if os.path.exists(script_path):
            print(f"🚀 Running {script_path}...")
            # বর্তমান পাইথন এনভায়রনমেন্ট ব্যবহার করে রান করা
            result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print(f"⚠️ Errors/Warnings: {result.stderr}")
        else:
            print("❌ Error: update_redforce.py not found inside the zip!")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
    
    finally:
        if os.path.exists(extract_folder):
            shutil.rmtree(extract_folder)
            print("🧹 Cleanup done: Secret files removed.")

if __name__ == "__main__":
    main()
