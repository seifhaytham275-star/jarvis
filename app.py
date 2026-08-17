                # اختيار الـ URL الصحيح والموديل المظبوط
                if provider == "Groq Console":
                    url = "https://api.groq.com/openai/v1/chat/completions"
                else:
                    url = "https://api.perplexity.ai/chat/completions"
                
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are Jarvis, created by the genius Seif. Respond in the user's language."},
                        {"role": "user", "content": prompt}
                    ]
                }
                
                res = requests.post(url, headers=headers, json=payload)
                
                if res.status_code == 200:
                    response = res.json()['choices'][0]['message']['content']
                elif res.status_code == 404:
                    response = "Error 404: The URL is incorrect. Check if you selected the right provider."
                else:
                    response = f"Error {res.status_code}: {res.text}"
