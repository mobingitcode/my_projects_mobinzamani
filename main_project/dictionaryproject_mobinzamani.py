# فراخوانی کتابخانه ها
import tkinter as tk 
from tkinter import ttk, messagebox , scrolledtext
import requests

# تعریف تابع برای جستجوی کلمه
def search_word () : 
    # دریافت کلمه ورودی و حذف فاصله های اضافه
    word = entry.get().strip()
    
    # در صورتی که کلمه ای وارد نشد به کاربر هشدار میدیم
    if not word : 
        messagebox.showwarning("Error" , "please enter the text")
        return
    
    # برای حذف موارد قبلی، جعبه متن را فعال می‌کنیم
    result_text.config(state=tk.NORMAL)
    # پاک کردن متن قبلی از خط اول تا آخر
    result_text.delete(1.0 , tk.END)
    # دوباره جعبه متن را غیرفعال می‌کنیم
    result_text.config(state=tk.DISABLED)
    
    # در قسمت وضعیت نشان دهنده ی انجام پروسه میباشد
    status_label.config(text="searching" , foreground="blue")
    # به روز رسانی برای جلوگیری از فریز شدن پنجره
    root.update_idletasks()
    
    # مدیریت خطای وصل نبودن به اینترنت
    try : 
        # ---------- ای پی آی اول برای گرفتن مواردی از قبیل آوا، مثال و ... ----------
        # دریافت اطلاعات از دیکشنری
        dict_url =  f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        dict_response = requests.get(dict_url)
        
        # اگر که مشکلی در ارتباط و دریافت اطلاعات بود
        if dict_response.status_code != 200 : 
            # باز کردن قسمت نتیجه و بیان پیدا نشدن کلمه در دیکشنری
            result_text.config(state=tk.NORMAL)
            result_text.insert(tk.END , " کلمه در دیکشنری پیدا نشد." ,"rtl")
            result_text.config(state = tk.DISABLED)
            # تغییر حالت قسمت وضعیت
            status_label.config(text = "This is the End !" , foreground="red")
            return
        
        # اگر اطلاعات دریافت شد، پاسخ را به دیکشنری تبدیل می‌کنیم
        data = dict_response.json()[0]
        
        # دریافت کلمه
        word_name = data.get("word", "not found")
        # دریافت آوا
        phonetic = data.get("phonetic", "not found")
        
        # دریافت اولین معنی از لیست معانی
        first_meaning = data["meanings"][0]
        # دریافت نوع کلمه (اسم، فعل، صفت و ...)
        part_of_speech = first_meaning.get("partOfSpeech", "not found")
        # دریافت اولین تعریف از لیست تعاریف
        first_def = first_meaning["definitions"][0]
        # دریافت متن تعریف
        definition = first_def.get("definition", "not found")
        # دریافت جمله نمونه
        example = first_def.get("example", "not found")

        # ---------- ای پی آی دوم: مترادف و متضاد ----------
        # لیست خالی برای مترادف‌ها
        synonyms = []
        # لیست خالی برای متضادها
        antonyms = []

        # شروع بلوک مدیریت خطا برای API دوم
        try : 
            # ساختن آدرس برای دریافت مترادف‌ها
            syn_url =  f"https://api.datamuse.com/words?rel_syn={word}&max=5"
            # ارسال درخواست برای مترادف‌ها
            syn_response = requests.get(syn_url)
            # اگر درخواست موفق بود
            if syn_response.status_code  == 200 : 
                # استخراج کلمات مترادف از پاسخ
                synonyms = [item["word"] for item in syn_response.json()]
            
            # ساختن آدرس برای دریافت متضادها (اصلاح شده به Datamuse)
            ant_url = f"https://api.datamuse.com/words?rel_ant={word}&max=5"
            # ارسال درخواست برای متضادها
            ant_response = requests.get(ant_url)
            # اگر درخواست موفق بود
            if ant_response.status_code == 200 : 
                # استخراج کلمات متضاد از پاسخ
                antonyms = [item["word"] for item in ant_response.json()]
        # اگر خطایی رخ داد، نادیده بگیر و ادامه بده
        except : 
            pass 

        # ---------- ای پی آی سوم: ترجمه فارسی ----------
        # مقدار پیش‌فرض برای ترجمه کلمه
        persian = "not found" 
        # مقدار پیش‌فرض برای ترجمه مثال
        example_fa = ""

        # شروع بلوک مدیریت خطا برای API سوم
        try : 
            # ساختن آدرس برای ترجمه کلمه
            trans_url = f"https://api.mymemory.translated.net/get?q={word}&langpair=en|fa"
            # ارسال درخواست ترجمه
            trans_response = requests.get(trans_url)
            # اگر درخواست موفق بود
            if trans_response.status_code == 200 : 
                # تبدیل پاسخ به دیکشنری
                trans_data = trans_response.json()
                # استخراج ترجمه فارسی از پاسخ
                persian = trans_data.get("responseData" ,  {}).get("translatedText", word)
                # اگر ترجمه پیدا نشد (خود کلمه برگشت)
                if persian.lower() == word.lower():
                    # مقدار را به "not found" تغییر بده
                    persian = "not found"
            
            # اگر مثال وجود داشت (یعنی "not found" نبود)
            if example != "not found" : 
                # ساختن آدرس برای ترجمه مثال
                ex_trans_url = f"https://api.mymemory.translated.net/get?q={example}&langpair=en|fa"
                # ارسال درخواست ترجمه مثال
                ex_trans_response = requests.get(ex_trans_url)
                # اگر درخواست موفق بود
                if ex_trans_response.status_code == 200:
                    # تبدیل پاسخ به دیکشنری
                    ex_trans_data = ex_trans_response.json()
                    # استخراج ترجمه مثال از پاسخ
                    example_fa = ex_trans_data.get("responseData", {}).get("translatedText", "")
        # اگر خطایی رخ داد، نادیده بگیر و ادامه بده
        except : 
            pass

        # ---------- ساخت خروجی ----------
        # شروع ساخت رشته خروجی
        output = f"{word_name}:کلمه\n\n"
        # اضافه کردن ترجمه فارسی
        output += f" ترجمه ی فارسی:{persian}\n\n"
        # اضافه کردن آوا
        output += f"{phonetic}:آوا\n\n"
        # اضافه کردن نوع کلمه
        output += f" {part_of_speech}:نوع کلمه\n\n"
        # اضافه کردن تعریف
        output += f"تعریف :{definition}\n\n"
        # اضافه کردن مثال
        output += f" مثال:{example}\n\n"
        # اضافه کردن مثال فارسی (اگر خالی بود، "not found")
        output += f" مثال فارسی:{example_fa if example_fa else 'not found'}\n\n"

        # اضافه کردن مترادف‌ها (اگر وجود داشتند)
        if synonyms:
            output += f"{', '.join(synonyms)}:مترادف ها\n\n"
        else:
            # اگر نبودند، "not found"
            output += " not found:مترادف ها\n\n"

        # اضافه کردن متضادها (اگر وجود داشتند)
        if antonyms:
            output += f"{', '.join(antonyms)}:متضاد ها\n\n"
        else:
            # اگر نبودند، "not found"
            output += " not found:متضاد ها\n\n"

        # نمایش نتیجه در جعبه متن
        result_text.config(state=tk.NORMAL)
        # درج خروجی با راست‌چین
        result_text.insert(tk.END, output, "rtl")
        # غیرفعال کردن جعبه متن
        result_text.config(state=tk.DISABLED)
        # تغییر نوار وضعیت به "جستجو کامل شد"
        status_label.config(text=	"Search completed", foreground="green")

    # اگر خطایی در کل فرآیند رخ داد
    except : 
        # نمایش پنجره خطا
        messagebox.showerror("خطا", f"مشکل در ارتباط با اینترنت یا سرور:")
        # تغییر نوار وضعیت به "خطا در جستجو"
        status_label.config(text="Search Error", foreground="red")


# ---------- ساخت پنجره اصلی ----------
# ایجاد پنجره اصلی
root = tk.Tk()
# تنظیم عنوان پنجره
root.title("dictionary")
# تنظیم اندازه پنجره (عرض × ارتفاع)
root.geometry("650x600")
# غیرفعال کردن قابلیت تغییر اندازه
root.resizable(width=False , height=False)

# ایجاد شیء استایل برای ویجت‌ها
style = ttk.Style()     
# تنظیم استایل دکمه‌ها (فاصله داخلی و فونت)
style.configure("TButton" , padding = 6 , font = ('Tahoma' , 10))
# تنظیم استایل برچسب‌ها (فونت)
style.configure("TLabel" , font = ('Tahoma' , 10))

# ---------- قاب بالایی (ورودی) ----------
# ایجاد قاب برای بخش ورودی
frame_top = ttk.Frame(root , padding= 10)
# قرار دادن قاب در پنجره (با عرض کامل)
frame_top.pack(fill = tk.X)

# ایجاد برچسب عنوان اصلی و استفاده از یونی کد برای اموجی
lbl_fan = ttk.Label(frame_top , text = "amzing dictionary \U0001F60A" , font=('Tahoma' , 15 , "bold"))
# قرار دادن برچسب در قاب (چسبیده به چپ)
lbl_fan.pack(anchor=tk.W)
# ایجاد برچسب راهنما
lbl_word = ttk.Label(frame_top , text = ":لطفا کلمه ی انگلیسی را وارد کنید\U0001F4DD")
# قرار دادن برچسب در قاب (چسبیده به راست)
lbl_word.pack(anchor=tk.E)

# ایجاد جعبه ورودی
entry = ttk.Entry(frame_top , font=('tahoma' , 12))
# قرار دادن جعبه ورودی با عرض کامل و فاصله عمودی
entry.pack(fill=tk.X , pady = 5)
# قرار دادن مکان‌نما در جعبه ورودی
entry.focus()

# ایجاد دکمه جستجو و استفاده از یونی کد
btn_search = ttk.Button(frame_top , text = "search \U0001F50D" , command = search_word)
# قرار دادن دکمه با فاصله عمودی
btn_search.pack(pady = 5)

# ---------- قاب پایینی (نمایش نتیجه) ----------
# ایجاد قاب برای نمایش نتیجه
frame_result = ttk.Frame(root , padding = 10)
# قرار دادن قاب در پنجره (با گسترش در هر دو جهت)
frame_result.pack(fill = tk.BOTH , expand=True)

# ایجاد جعبه متن با قابلیت اسکرول
result_text = scrolledtext.ScrolledText(
    frame_result , 
    wrap = tk.WORD,  # شکستن خط در انتهای کلمات برای اینکه سر هر خط جدا نشه
    font = ('Tahoma' , 11) ,  # فونت متن
    state = tk.DISABLED,  # غیرفعال (فقط نمایشی)
    height = 20  # ارتفاع اولیه
)
# تنظیم تگ راست‌چین برای متن
result_text.tag_configure("rtl", justify='right')
# قرار دادن جعبه متن در قاب (با گسترش)
result_text.pack(fill=tk.BOTH , expand = True )

# ---------- نوار وضعیت ----------
# ایجاد نوار وضعیت در پایین پنجره
# relief میاد و یک حالت تو رفتگی میده
status_label = ttk.Label(root , text = "ready" , relief=tk.SUNKEN , anchor = tk.W)
# قرار دادن نوار وضعیت در پایین با عرض کامل
status_label.pack(side = tk.BOTTOM , fill = tk .X , padx = 5 , pady = 5)

# اجرای حلقه اصلی برنامه
root.mainloop()

# ========== مثال ساختار JSON دریافتی از API اول (دیکشنری) برای کلمه "book" ==========
# {
#     "word": "book",
#     "phonetic": "/bʊk/",
#     "meanings": [
#         {
#             "partOfSpeech": "noun",
#             "definitions": [
#                 {
#                     "definition": "a set of written pages fastened together along one side and encased between protective covers",
#                     "example": "I'm reading a book"
#                 }
#             ]
#         }
#     ]
# }

# ========== مثال ساختار JSON دریافتی از API دوم (مترادف‌ها) برای کلمه "happy" ==========
# [
#     {"word": "glad", "score": 100},
#     {"word": "joyful", "score": 90},
#     {"word": "cheerful", "score": 80},
#     {"word": "delighted", "score": 70},
#     {"word": "pleased", "score": 60}
# ]

# ========== مثال ساختار JSON دریافتی از API سوم (ترجمه) برای کلمه "book" ==========
# {
#     "responseData": {
#         "translatedText": "کتاب"
#     },
#     "responseStatus": 200
# }