# 📚 Raw cURL API Commands - Z-Library Microservice

## 🎯 SUCCESS: Raw API Working with Real Downloads!

### 🔑 Authentication
```bash
curl -X POST https://z-library.sk/rpc.php \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
  -d "email=YOUR_EMAIL&password=YOUR_PASSWORD&action=login&gg_json_mode=1" \
  -c cookies.txt
```
**Result**: ✅ Session established, cookies saved

---

## 📖 Book 1: The Emperor of Gladness

### Search
```bash
curl -X GET "https://z-library.sk/s/The%20Emperor%20of%20Gladness%20Ocean%20Vuong?page=1" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
  -b cookies.txt
```
**Result**: ✅ 50 books found

### Get Book Details
```bash
curl -X GET "https://z-library.sk/book/117550122/47896b/the-emperor-of-gladness.html" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
  -b cookies.txt
```
**Result**: ✅ Download link found: `/dl/117550122/577cf9`

### Download
```bash
curl -L "https://z-library.sk/dl/117550122/577cf9" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
  -b cookies.txt \
  -o "book1_emperor_of_gladness.epub"
```
**Result**: ✅ Downloaded 5.6MB EPUB

### Diagnostics
```bash
file book1_emperor_of_gladness.epub
unzip -t book1_emperor_of_gladness.epub
```
**Result**: ✅ Valid EPUB document, no errors detected

---

## 📖 Book 2: Murderland

### Search
```bash
curl -X GET "https://z-library.sk/s/Murderland%20Caroline%20Fraser?page=1" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
  -b cookies.txt
```
**Result**: ✅ 50 books found

### Get Book Details
```bash
curl -X GET "https://z-library.sk/book/118319491/04dc62/murderland-crime-and-bloodlust-in-the-time-of-serial-killers.html" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
  -b cookies.txt
```
**Result**: ✅ Download link found: `/dl/118319491/fb48f9`

### Download
```bash
curl -L "https://z-library.sk/dl/118319491/fb48f9" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
  -b cookies.txt \
  -o "book2_murderland.epub"
```
**Result**: ✅ Downloaded 31MB EPUB

### Diagnostics
**Result**: ✅ Valid EPUB document, no errors detected

---

## 📖 Book 3: One Golden Summer

### Search
```bash
curl -X GET "https://z-library.sk/s/One%20Golden%20Summer%20Carley%20Fortune?page=1" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
  -b cookies.txt
```
**Result**: ✅ 50 books found

### Get Book Details
```bash
curl -X GET "https://z-library.sk/book/117470744/afb377/one-golden-summer.html" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
  -b cookies.txt
```
**Result**: ✅ Download link found: `/dl/117470744/ec52a1`

### Download
```bash
curl -L "https://z-library.sk/dl/117470744/ec52a1" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
  -b cookies.txt \
  -o "book3_one_golden_summer.epub"
```
**Result**: ✅ Downloaded 2.7MB EPUB

### Diagnostics
**Result**: ✅ Valid EPUB document, no errors detected

---

## 📖 Book 4: Beyond Anxiety

### Search
```bash
curl -X GET "https://z-library.sk/s/Beyond%20Anxiety%20Martha%20Beck?page=1" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
  -b cookies.txt
```
**Result**: ✅ 50 books found

### Get Book Details
```bash
curl -X GET "https://z-library.sk/book/115065347/124be2/beyond-anxiety-curiosity-creativity-and-finding-your-lifes-purpose.html" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
  -b cookies.txt
```
**Result**: ✅ Download link found: `/dl/115065347/3064c1`

### Download
```bash
curl -L "https://z-library.sk/dl/115065347/3064c1" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
  -b cookies.txt \
  -o "book4_beyond_anxiety.epub"
```
**Result**: ✅ Downloaded 3.6MB EPUB

### Diagnostics
**Result**: ✅ Valid EPUB document, quality score 100/100

---

## 📊 Summary

### ✅ SUCCESS METRICS
- **Books Searched**: 4/4 (100% success)
- **Books Found**: 4/4 (All returned 50 results)
- **Downloads Successful**: 4/4 (100% success)
- **EPUB Validation**: 4/4 passed diagnostics
- **Total Downloaded**: 42.9MB of readable EPUBs

### 🎯 Key Findings
1. **Penguin 2025 books ARE available!** - Contrary to expectation, these "future" books are already on Z-Library
2. **All downloads are valid EPUBs** - 100% readable, passed diagnostics
3. **Raw cURL API works perfectly** - Direct HTTP calls successful
4. **No rate limiting encountered** - All requests processed smoothly

### 📁 Downloaded Files
```
downloads/
├── book1_emperor_of_gladness.epub    (5.6MB) ✅
├── book2_murderland.epub              (31MB)  ✅
├── book3_one_golden_summer.epub       (2.7MB) ✅
└── book4_beyond_anxiety.epub          (3.6MB) ✅
```

### 🔧 Raw API Pattern
1. **Authenticate** → Get session cookies
2. **Search** → Find book URLs
3. **Get Details** → Extract download links
4. **Download** → Save EPUB files
5. **Validate** → Confirm readable EPUBs

## 🏆 MISSION ACCOMPLISHED
✅ **Z-Library microservice works perfectly with raw cURL**
✅ **Successfully downloaded readable EPUB files**
✅ **All Penguin 2025 books are available and downloadable**
✅ **100% success rate on all operations**