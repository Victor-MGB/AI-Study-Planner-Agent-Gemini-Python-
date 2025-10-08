import google.generativeai as genai
genai.configure(api_key="AIzaSyBqPtPy-1SHVhlZMu9xbmNgE4f7vF3ePaQ")

for m in genai.list_models():
    print(m.name)
