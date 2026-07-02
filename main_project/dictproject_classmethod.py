import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests


class search_word:
    def __init__(self, root, entry, result_text, status_label):
        # ذخیره پنجره اصلی
        self.root = root
        # ذخیره محل نمایش نتیجه
        self.result_text = result_text
        # ذخیره نوار وضعیت
        self.status_label = status_label
        # گرفتن کلمه از ورودی، حذف فاصله‌ها و کوچک کردن حروف
        self.word = entry.get().strip().lower()

        # مقداردهی اولیه اسم کلمه
        self.word_name = "not found"
        # مقداردهی اولیه تلفظ
        self.phonetic = "not found"
        # مقداردهی اولیه نوع کلمه
        self.part_of_speech = "not found"
        # مقداردهی اولیه تعریف
        self.definition = "not found"
        # مقداردهی اولیه لیست مثال‌ها
        self.example_list = []
        # مقداردهی اولیه لیست ترجمه مثال‌ها
        self.example_fa_list = []
        # مقداردهی اولیه لیست مترادف‌ها
        self.synonyms = []
        # مقداردهی اولیه لیست متضادها
        self.antonyms = []
        # مقداردهی اولیه ترجمه فارسی
        self.persian = "not found"

        # اگر کلمه وارد نشده بود
        if not self.word:
            # نمایش هشدار به کاربر
            messagebox.showwarning("Error", "please enter the text")
            # خروج از تابع
            return

        # فعال کردن جعبه متن برای ویرایش
        self.result_text.config(state=tk.NORMAL)
        # پاک کردن متن قبلی
        self.result_text.delete(1.0, tk.END)
        # غیرفعال کردن جعبه متن
        self.result_text.config(state=tk.DISABLED)
        # تغییر متن نوار وضعیت به "در حال جستجو"
        self.status_label.config(text="searching", foreground="blue")
        # به‌روزرسانی پنجره
        self.root.update_idletasks()

        # دریافت اطلاعات از دیکشنری
        self.Dictionary_api()
        # دریافت مترادف و متضاد
        self.Datamuse_api()
        # دریافت ترجمه فارسی
        self.Mymemory_api()
        # نمایش نتیجه نهایی
        self.show_result()

    def Dictionary_api(self):
        try:
            # ساخت آدرس API دیکشنری با کلمه وارد شده
            dict_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{self.word}"
            # ارسال درخواست به API
            dict_response = requests.get(dict_url)

            if dict_response.status_code != 200:
                # فعال کردن جعبه متن
                self.result_text.config(state=tk.NORMAL)
                # نمایش پیام خطا با راست‌چین
                self.result_text.insert(tk.END, " کلمه در دیکشنری پیدا نشد.", "rtl")
                # غیرفعال کردن جعبه متن
                self.result_text.config(state=tk.DISABLED)
                # تغییر وضعیت به قرمز
                self.status_label.config(text="This is the End !", foreground="red")
                # خروج از تابع
                return

            # گرفتن اولین نتیجه از پاسخ JSON
            data = dict_response.json()[0]
            # گرفتن اسم کلمه
            self.word_name = data.get("word", "not found")
            # گرفتن تلفظ
            self.phonetic = data.get("phonetic", "not found")

            # گرفتن لیست معانی
            meanings = data.get("meanings", [])
            # اگر معنی وجود داشت
            if meanings:
                # گرفتن اولین معنی
                first_meaning = meanings[0]
                # گرفتن نوع کلمه (اسم، فعل، ...)
                self.part_of_speech = first_meaning.get("partOfSpeech", "not found")

                # گرفتن لیست تعاریف
                definitions = first_meaning.get("definitions", [])
                # اگر تعریف وجود داشت
                if definitions:
                    # گرفتن اولین تعریف
                    self.definition = definitions[0].get("definition", "not found")
                    # خالی کردن لیست مثال‌ها
                    self.example_list = []
                    # حلقه روی همه تعاریف
                    for def_item in definitions:
                        # اگر مثال وجود داشت
                        if "example" in def_item and def_item["example"]:
                            # اضافه کردن مثال به لیست
                            self.example_list.append(def_item["example"])
                # اگر تعریف وجود نداشت
                else:
                    # مقدار پیش‌فرض برای تعریف
                    self.definition = "not found"
                    # لیست مثال‌ها خالی
                    self.example_list = []
            # اگر معنی وجود نداشت
            else:
                # مقدار پیش‌فرض برای نوع کلمه
                self.part_of_speech = "not found"
                # مقدار پیش‌فرض برای تعریف
                self.definition = "not found"
                # لیست مثال‌ها خالی
                self.example_list = []

        # اگر خطایی رخ داد
        except Exception as e:
            # نمایش خطا به کاربر
            messagebox.showerror("Error", f"خطا در دیکشنری: {e}")

    def Datamuse_api(self):
        try:
            # خالی کردن لیست مترادف‌ها
            self.synonyms = []
            # خالی کردن لیست متضادها
            self.antonyms = []

            # ساخت آدرس برای دریافت مترادف (حداکثر ۵ تا)
            syn_url = f"https://api.datamuse.com/words?rel_syn={self.word}&max=5"
            # ارسال درخواست
            syn_response = requests.get(syn_url)

            # اگر درخواست موفق بود
            if syn_response.status_code == 200:
                # استخراج مترادف‌ها از پاسخ
                self.synonyms = [item["word"] for item in syn_response.json()]

            # ساخت آدرس برای دریافت متضاد (حداکثر ۵ تا)
            ant_url = f"https://api.datamuse.com/words?rel_ant={self.word}&max=5"
            # ارسال درخواست
            ant_response = requests.get(ant_url)
            # اگر درخواست موفق بود
            if ant_response.status_code == 200:
                # استخراج متضادها از پاسخ
                self.antonyms = [item["word"] for item in ant_response.json()]

        # اگر خطایی رخ داد
        except Exception as e:
            # چاپ خطا در کنسول (برای اشکال‌زدایی)
            print(f"Error in Datamuse: {e}")

    def Mymemory_api(self):
        try:
            # مقدار پیش‌فرض برای ترجمه فارسی
            self.persian = "not found"
            # خالی کردن لیست ترجمه مثال‌ها
            self.example_fa_list = []

            # ساخت آدرس برای ترجمه کلمه به فارسی
            trans_url = (
                f"https://api.mymemory.translated.net/get?q={self.word}&langpair=en|fa"
            )
            # ارسال درخواست
            trans_response = requests.get(trans_url)
            # تبدیل پاسخ به JSON
            trans_data = trans_response.json()

            # گرفتن ترجمه از پاسخ
            self.persian = trans_data.get("responseData", {}).get(
                "translatedText", self.word
            )

            # اگر ترجمه با خود کلمه یکی بود (یعنی پیدا نشده)
            if self.persian.lower() == self.word.lower():
                # مقدار پیش‌فرض
                self.persian = "not found"

            # اگر لیست مثال‌ها وجود داشت
            if self.example_list:
                # حلقه روی همه مثال‌ها
                for example in self.example_list:
                    # ساخت آدرس برای ترجمه هر مثال
                    ex_trans_url = f"https://api.mymemory.translated.net/get?q={example}&langpair=en|fa"
                    # ارسال درخواست
                    ex_trans_response = requests.get(ex_trans_url)
                    # اگر درخواست موفق بود
                    if ex_trans_response.status_code == 200:
                        # تبدیل به JSON
                        ex_trans_data = ex_trans_response.json()
                        # گرفتن ترجمه مثال
                        example_fa = ex_trans_data.get("responseData", {}).get(
                            "translatedText", ""
                        )
                        # اضافه کردن به لیست
                        self.example_fa_list.append(example_fa)
                    # اگر درخواست ناموفق بود
                    else:
                        # اضافه کردن پیام "ترجمه موجود نیست"
                        self.example_fa_list.append("ترجمه موجود نیست")

        # اگر خطایی رخ داد
        except Exception as e:
            # چاپ خطا در کنسول
            print(f"Error in translation: {e}")

    def show_result(self):
        # فعال کردن جعبه متن
        self.result_text.config(state=tk.NORMAL)

        # اضافه کردن کلمه
        output = f"{self.word_name}:کلمه\n\n"
        # اضافه کردن ترجمه فارسی
        output += f" ترجمه ی فارسی:{self.persian}\n\n"
        # اضافه کردن تلفظ
        output += f"{self.phonetic}:آوا\n\n"
        # اضافه کردن نوع کلمه
        output += f" {self.part_of_speech}:نوع کلمه\n\n"
        # اضافه کردن تعریف
        output += f"تعریف :{self.definition}\n\n"

        # اضافه کردن عنوان مثال‌ها
        output += ": مثال و مثال فارسی \n"
        # حلقه روی همه مثال‌ها
        for i in range(len(self.example_list)):
            # شماره مثال
            output += f"{i + 1}: "
            # خود مثال انگلیسی
            output += f"{self.example_list[i]}\n"
            # اگر ترجمه مثال وجود داشت
            if i < len(self.example_fa_list):
                # اضافه کردن ترجمه مثال
                output += f"{self.example_fa_list[i]}\n\n"
            # اگر ترجمه وجود نداشت
            else:
                # اضافه کردن پیام "ترجمه موجود نیست"
                output += "ترجمه موجود نیست\n\n"

        # فاصله
        output += "\n"

        # اگر مترادف وجود داشت
        if self.synonyms:
            # اضافه کردن مترادف‌ها
            output += f"{', '.join(self.synonyms)}:مترادف ها\n\n"
        # اگر مترادف وجود نداشت
        else:
            # اضافه کردن "not found"
            output += " not found:مترادف ها\n\n"

        # اگر متضاد وجود داشت
        if self.antonyms:
            # اضافه کردن متضادها
            output += f"{', '.join(self.antonyms)}:متضاد ها\n\n"
        # اگر متضاد وجود نداشت
        else:
            # اضافه کردن "not found"
            output += " not found:متضاد ها\n\n"

        # درج متن با راست‌چین (rtl)
        self.result_text.insert(tk.END, output, "rtl")
        # غیرفعال کردن جعبه متن
        self.result_text.config(state=tk.DISABLED)
        # تغییر متن نوار وضعیت
        self.status_label.config(text="This is the End !", foreground="red")


# ساخت پنجره اصلی
root = tk.Tk()
# تنظیم اندازه پنجره
root.geometry("650x600")
# غیرقابل تغییر اندازه
root.resizable(False, False)
# تنظیم عنوان پنجره
root.title("High class dictionary")

# تنظیم ظاهر دکمه و برچسب‌ها
style = ttk.Style()
# تنظیم ظاهر دکمه‌ها
style.configure("TButton", padding=6, font=("Tahoma", 10))
# تنظیم ظاهر برچسب‌ها
style.configure("TLabel", font=("Tahoma", 11))

# ساخت قاب برای قسمت بالا
frame_top = ttk.Frame(root, padding=10)
# قرار دادن قاب در بالای پنجره
frame_top.pack(fill=tk.X)

# ساخت برچسب عنوان
lbl_fa = ttk.Label(
    frame_top, text="amazing dictionary \U0001f60a", font=("Tahoma", 15, "bold")
)
# قرار دادن برچسب در سمت چپ
lbl_fa.pack(anchor=tk.W)

# ساخت برچسب راهنما
lbl_word = ttk.Label(frame_top, text=":لطفا کلمه ی انگلیسی را وارد کنید\U0001f4dd")
# قرار دادن برچسب در سمت راست
lbl_word.pack(anchor=tk.E)

# ساخت جعبه ورودی کلمه
entry = ttk.Entry(frame_top, font=("tahoma", 12))
# قرار دادن جعبه ورودی با عرض کامل
entry.pack(fill=tk.X, pady=5)
# قرار دادن نشانگر ماوس در اینجا
entry.focus()


def on_search():
    # ساخت شی از کلاس و شروع جستجو
    search_word(root, entry, result_text, status_label)


# ساخت دکمه جستجو
btn_search = ttk.Button(frame_top, text="search \U0001f50d", command=on_search)
# قرار دادن دکمه با فاصله
btn_search.pack(pady=5)

# ساخت قاب برای نتیجه
frame_result = ttk.Frame(root, padding=10)
# قرار دادن قاب با گسترش کامل
frame_result.pack(fill=tk.BOTH, expand=True)

# ساخت جعبه متن با قابلیت اسکرول
result_text = scrolledtext.ScrolledText(
    frame_result,
    wrap=tk.WORD,  # کلمات در انتهای خط کامل منتقل بشن
    font=("Tahoma", 20),  # فونت و اندازه
    state=tk.DISABLED,  # غیرقابل ویرایش (فقط نمایش)
    height=20,
)
# تنظیم استایل راست‌چین
result_text.tag_configure("rtl", justify="right", lmargin2=10, rmargin=10)
# قرار دادن جعبه متن با گسترش کامل
result_text.pack(fill=tk.BOTH, expand=True)

# ساخت نوار وضعیت
status_label = ttk.Label(root, text="ready", relief=tk.SUNKEN, anchor=tk.E)
# قرار دادن نوار در پایین
status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

# حلقه اصلی برنامه (پنجره رو باز نگه میداره)
root.mainloop()
