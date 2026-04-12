import zipfile
import os
import shutil

# কনফিগারেশন
zip_filename = 'redforce_main.zip'
extract_folder = 'temp_work' # এখানে ফাইলগুলো আনজিপ হবে
zip_password = os.getenv("ZIP_PASS") # এটি GitHub Secret থেকে আসবে

def main():
    if not zip_password:
        print("❌ Error: ZIP_PASS environment variable is not set.")
        return

    try:
        # ১. জিপ ফাইল খোলা
        with zipfile.ZipFile(zip_filename, 'r') as zf:
            zf.extractall(path=extract_folder, pwd=zip_password.encode('utf-8'))
            print("✅ Successfully decrypted and extracted files.")

        # ২. মূল স্ক্রিপ্টটি রান করা
        # আপনার স্ক্রিপ্টের নাম যদি update_redforce.py হয়
        script_path = os.path.join(extract_folder, "update_redforce.py")
        
        if os.path.exists(script_path):
            print(f"🚀 Running {script_path}...")
            os.system(f"python {script_path}")
        else:
            print("❌ Error: update_redforce.py not found inside the zip!")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
    
    finally:
        # ৩. কাজ শেষ হলে সব ডিলিট করে দেওয়া (নিরাপত্তার জন্য)
        if os.path.exists(extract_folder):
            shutil.rmtree(extract_folder)
            print("🧹 Cleanup done: Secret files removed.")

if __name__ == "__main__":
    main()
