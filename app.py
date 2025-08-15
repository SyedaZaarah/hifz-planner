from flask import Flask, render_template, request, jsonify
import math
import json
from datetime import datetime, timedelta
import gradio as gr

def greet(name):
    return f"Hello {name}!"

iface = gr.Interface(fn=greet, inputs="text", outputs="text")
iface.launch()


app = Flask(__name__)

class HifzPlannerAI:
    def __init__(self):
        # Average pages per Juz (approximately 20 pages)
        self.pages_per_juz = 20
        
        # Time estimates based on your specifications
        self.time_per_new_page = 60  # 1 hour per page for new memorization
        self.time_per_half_juz_revision = 60  # 1 hour for revision of half Juz
        
        # Memorization rates based on experience level
        self.daily_memorization_rates = {
            'under_2_juz': 5,     # 5 lines/day (< 2 Juz)
            '2_to_5_juz': 7,      # 7 lines/day (2-5 Juz)  
            'over_5_juz': 15      # 1 page/day = 15 lines/day (> 5 Juz)
        }
    
    def determine_experience_level(self, juz_completed):
        """Determine experience level based on Juz completed"""
        if juz_completed < 2:
            return 'under_2_juz'
        elif juz_completed <= 5:
            return '2_to_5_juz'
        else:
            return 'over_5_juz'
    
    def get_revision_chunk_size(self, juz_completed):
        """Determine revision chunk size based on total Juz completed"""
        if juz_completed < 5:
            return 0.5  # Half Juz
        elif juz_completed < 10:
            return 1.0  # Full Juz
        else:
            return 2.0  # Two Juz

    def generate_plan(self, juz_completed, juz_to_memorize):
        """Generate Hifz plan based on current status and target"""
        
        # Calculate pages to memorize
        pages_to_memorize = juz_to_memorize * self.pages_per_juz
        
        # Determine experience level
        experience_level = self.determine_experience_level(juz_completed)
        daily_lines_rate = self.daily_memorization_rates[experience_level]
        
        # Convert lines to pages per day
        lines_per_page = 15
        daily_pages_rate = daily_lines_rate / lines_per_page
        
        # Calculate days needed for new memorization
        days_for_new_memorization = pages_to_memorize / daily_pages_rate
        
        # Calculate daily new memorization time
        daily_new_time_hours = daily_pages_rate * (self.time_per_new_page / 60)
        
        # Calculate revision requirements
        if juz_completed > 0:
            revision_chunk_size = self.get_revision_chunk_size(juz_completed)
            
            # Time for one revision session
            time_per_revision_session = revision_chunk_size * (self.time_per_half_juz_revision / 60)
            
            # How many revision sessions needed to cover all completed Juz
            total_revision_sessions = juz_completed / revision_chunk_size
            
            # Daily revision time (assuming 7-day revision cycle)
            daily_revision_time_hours = (total_revision_sessions * time_per_revision_session) / 7
            
        else:
            daily_revision_time_hours = 0
            revision_chunk_size = 0
            time_per_revision_session = 0
        
        # Total daily time
        total_daily_hours = daily_new_time_hours + daily_revision_time_hours
        
        return {
            'juz_completed': juz_completed,
            'juz_to_memorize': juz_to_memorize,
            'experience_level': experience_level,
            'daily_plan': {
                'new_lines': daily_lines_rate,
                'new_pages': round(daily_pages_rate, 2),
                'new_time_hours': round(daily_new_time_hours, 1),
                'revision_time_hours': round(daily_revision_time_hours, 1),
                'total_time_hours': round(total_daily_hours, 1),
                'revision_chunk_size': revision_chunk_size
            },
            'completion': {
                'total_days': round(days_for_new_memorization),
                'total_pages': pages_to_memorize
            },
            'recommendations': self.generate_recommendations(experience_level, juz_completed, juz_to_memorize)
        }
    
    def generate_recommendations(self, experience_level, juz_completed, juz_to_memorize):
        """Generate personalized recommendations"""
        recommendations = []
        
        # Experience-based recommendations
        if experience_level == 'under_2_juz':
            recommendations.extend([
                f"🎯 Beginner Level: 5 lines/day is perfect for building strong foundations",
                "📚 Focus on proper pronunciation and understanding before speed",
                "👥 Work with a qualified teacher for corrections and guidance"
            ])
        elif experience_level == '2_to_5_juz':
            recommendations.extend([
                f"📈 Intermediate Level: 7 lines/day maintains good steady progress", 
                "🔄 Balance new memorization with regular revision",
                "📊 You're building good momentum - stay consistent"
            ])
        else:
            recommendations.extend([
                f"🚀 Advanced Level: 1 page (15 lines)/day shows excellent capability",
                "👨‍🏫 Consider teaching others to reinforce your memory",
                "🎯 Focus on perfecting Tajweed while memorizing"
            ])
        
        # Revision recommendations
        if juz_completed < 5:
            recommendations.append(f"🔄 Revision: Review {0.5} Juz daily in your revision time")
        elif juz_completed < 10:
            recommendations.append(f"🔄 Revision: Review 1 full Juz daily in your revision time")
        else:
            recommendations.append(f"🔄 Revision: Review 2 Juz daily in your revision time")
        
        # General recommendations
        recommendations.extend([
            "🌅 Best times: After Fajr or before Maghrib for memorization",
            "💪 Consistency is key - daily practice brings success",
            "🤲 Always begin with Bismillah and make dua for success"
        ])
        
        return recommendations

# Initialize AI planner
ai_planner = HifzPlannerAI()

class IslamicKnowledgeBot:
    def __init__(self):
        # Islamic knowledge database (simplified for demo)
        self.knowledge_base = {
            "5 pillars": {
                "keywords": ["pillar", "pillars", "5", "five", "foundation"],
                "answer": """🕌 **The Five Pillars of Islam:**

1. **Shahada (شهادة)** - Declaration of Faith
   - "La ilaha illa Allah, Muhammad rasul Allah"
   - "There is no god but Allah, and Muhammad is His messenger"

2. **Salah (صلاة)** - Prayer
   - Five daily prayers: Fajr, Dhuhr, Asr, Maghrib, Isha
   - Performed facing the Qiblah (direction of Kaaba)

3. **Zakat (زكاة)** - Charity/Almsgiving
   - Obligatory charity for those who can afford it
   - Usually 2.5% of savings given to the poor

4. **Sawm (صوم)** - Fasting
   - Fasting during the month of Ramadan
   - From dawn (Fajr) to sunset (Maghrib)

5. **Hajj (حج)** - Pilgrimage
   - Pilgrimage to Mecca once in a lifetime if able
   - Performed during the Islamic month of Dhul Hijjah"""
            },
            "wudu": {
                "keywords": ["wudu", "ablution", "wash", "clean", "purify"],
                "answer": """🚿 **Steps for Wudu (Ablution):**

1. **Intention (Niyyah)** - Make intention in your heart
2. **Say Bismillah** - "In the name of Allah"
3. **Wash hands** - Three times up to the wrists
4. **Rinse mouth** - Three times, swish water around
5. **Rinse nose** - Three times, sniff water and blow out
6. **Wash face** - Three times, from hairline to chin
7. **Wash arms** - Right arm three times up to elbow, then left
8. **Wipe head** - Once, with wet hands
9. **Wipe ears** - Inside and outside with wet fingers
10. **Wash feet** - Right foot three times up to ankle, then left

**Dua after Wudu:**
"Ashhadu an la ilaha illa Allah wahdahu la sharika lah, wa ashhadu anna Muhammadan abduhu wa rasuluh"

*I bear witness that there is no god but Allah alone, and I bear witness that Muhammad is His servant and messenger.*"""
            },
            "al-fatiha": {
                "keywords": ["fatiha", "opening", "surah 1", "first surah"],
                "answer": """📖 **Surah Al-Fatiha (The Opening):**

**Arabic:**
بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ
الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ
الرَّحْمَٰنِ الرَّحِيمِ
مَالِكِ يَوْمِ الدِّينِ
إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ
اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ
صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ

**Translation:**
In the name of Allah, the Most Gracious, the Most Merciful.
All praise is due to Allah, Lord of the worlds.
The Most Gracious, the Most Merciful.
Master of the Day of Judgment.
You alone we worship, and You alone we ask for help.
Guide us to the straight path.
The path of those You have blessed, not of those who have incurred Your wrath, nor of those who have gone astray.

**Significance:** This is the opening chapter of the Quran, recited in every unit (rakah) of prayer. It's called "The Mother of the Quran" and contains the essence of Islamic belief."""
            },
            "forgiveness": {
                "keywords": ["forgiveness", "dua", "forgive", "repentance", "taubah"],
                "answer": """🤲 **Duas for Forgiveness:**

**1. Sayyid al-Istighfar (Master of Seeking Forgiveness):**

**Arabic:**
اللَّهُمَّ أَنْتَ رَبِّي لَا إِلَٰهَ إِلَّا أَنْتَ خَلَقْتَنِي وَأَنَا عَبْدُكَ وَأَنَا عَلَىٰ عَهْدِكَ وَوَعْدِكَ مَا اسْتَطَعْتُ أَعُوذُ بِكَ مِنْ شَرِّ مَا صَنَعْتُ أَبُوءُ لَكَ بِنِعْمَتِكَ عَلَيَّ وَأَبُوءُ بِذَنْبِي فَاغْفِرْ لِي فَإِنَّهُ لَا يَغْفِرُ الذُّنُوبَ إِلَّا أَنْتَ

**Transliteration:**
Allahumma anta rabbi la ilaha illa anta, khalaqtani wa ana abduka, wa ana ala ahdika wa wa'dika mastata't, a'udhu bika min sharri ma sana't, abu'u laka bi ni'matika alayya wa abu'u bi dhanbi, faghfir li fa innahu la yaghfiru adh-dhunuba illa ant.

**Translation:**
O Allah, You are my Lord, there is no god but You. You created me and I am Your servant. I try my best to keep my covenant with You and to live in hope of Your promise. I seek refuge in You from the evil of what I have done. I acknowledge Your blessing upon me, and I acknowledge my sin. So forgive me, for indeed none can forgive sins except You.

**2. Simple Istighfar:**
أَسْتَغْفِرُ اللَّهَ - Astaghfirullah (I seek forgiveness from Allah)

**Benefit:** Prophet Muhammad (ﷺ) said whoever recites Sayyid al-Istighfar during the day with conviction and dies that day will enter Paradise."""
            }
        }

    def get_response(self, question):
        """Generate response based on Islamic knowledge"""
        question_lower = question.lower()
        
        # Search for matching topics
        for topic, data in self.knowledge_base.items():
            for keyword in data["keywords"]:
                if keyword in question_lower:
                    return data["answer"]
        
        # Default responses for common Islamic topics
        if any(word in question_lower for word in ["prayer", "salah", "namaz"]):
            return """🕌 **About Salah (Prayer):**

Muslims are required to pray 5 times daily:

• **Fajr** - Dawn prayer (2 rakah)
• **Dhuhr** - Noon prayer (4 rakah) 
• **Asr** - Afternoon prayer (4 rakah)
• **Maghrib** - Sunset prayer (3 rakah)
• **Isha** - Night prayer (4 rakah)

Each prayer has specific times and involves recitation of Quran verses, including Surah Al-Fatiha. Prayer is performed facing the Qiblah (direction of Kaaba in Mecca).

Would you like to know about prayer times, how to perform prayer, or specific prayers?"""

        elif any(word in question_lower for word in ["quran", "qur'an", "holy book"]):
            return """📖 **About the Quran:**

The Quran is the holy book of Islam, revealed to Prophet Muhammad (ﷺ) over 23 years. Key facts:

• **114 chapters** (Surahs) with 6,236 verses (Ayahs)
• **30 sections** (Juz/Para) for easy reading
• **Written in Arabic** - considered the direct word of Allah
• **Memorization** (Hifz) is a blessed act
• **Recitation** brings immense rewards

The Quran covers guidance for all aspects of life, stories of prophets, laws, morality, and spirituality.

What specific aspect of the Quran would you like to know about?"""

        elif any(word in question_lower for word in ["hadith", "sunnah", "prophet", "muhammad"]):
            return """📚 **About Hadith and Sunnah:**

• **Hadith** - Recorded sayings, actions, and approvals of Prophet Muhammad (ﷺ)
• **Sunnah** - The way of life and practices of the Prophet (ﷺ)

**Major Hadith Collections:**
1. Sahih Bukhari
2. Sahih Muslim  
3. Sunan Abu Dawood
4. Jami at-Tirmidhi
5. Sunan an-Nasa'i
6. Sunan Ibn Majah

Hadith help us understand how to implement Quranic teachings in daily life. They provide context and practical examples of Islamic principles.

Would you like to know about specific hadiths or topics?"""

        elif any(word in question_lower for word in ["ramadan", "fasting", "sawm"]):
            return """🌙 **About Ramadan and Fasting:**

**Ramadan** is the 9th month of the Islamic calendar, a time of:

• **Fasting (Sawm)** from dawn to sunset
• **Increased prayer** and Quran recitation
• **Charity (Zakat)** and helping others
• **Self-reflection** and spiritual growth

**Fasting Rules:**
- No food, drink, or intimate relations from Fajr to Maghrib
- Begin with Suhur (pre-dawn meal)
- Break fast with Iftar at sunset
- Exempt: sick, traveling, pregnant, elderly

**Benefits:** Spiritual purification, empathy for the poor, self-discipline, and increased God-consciousness (Taqwa).

**Laylat al-Qadr** (Night of Power) falls in the last 10 nights of Ramadan."""

        else:
            return """🤖 I'm here to help with Islamic knowledge! I can assist you with:

• **Religious practices** - Prayer, fasting, pilgrimage, charity
• **Quran and Hadith** - Verses, interpretations, stories
• **Islamic beliefs** - Articles of faith, prophets, Islamic history
• **Duas and supplications** - For various occasions and needs
• **Islamic calendar** - Important dates and events
• **Moral guidance** - Islamic ethics and values

Please ask me a specific question about Islam, and I'll do my best to help you with authentic Islamic knowledge.

Example questions:
- "How do I perform Salah?"
- "What is the significance of Surah Al-Baqarah?"
- "Tell me about the Prophet's companions"
- "What are the major sins in Islam?"

What would you like to learn about today?"""

# Initialize Islamic bot
islamic_bot = IslamicKnowledgeBot()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_plan', methods=['POST'])
def generate_plan():
    try:
        data = request.json
        juz_completed = int(data['juz_completed'])
        juz_to_memorize = int(data['juz_to_memorize'])
        
        # Validation
        if juz_completed < 0 or juz_completed > 30:
            return jsonify({'error': 'Completed Juz must be between 0 and 30'}), 400
            
        if juz_to_memorize < 1:
            return jsonify({'error': 'Must want to memorize at least 1 Juz'}), 400
            
        if juz_completed + juz_to_memorize > 30:
            return jsonify({'error': 'Total cannot exceed 30 Juz (full Quran)'}), 400
        
        # Generate plan
        plan = ai_planner.generate_plan(juz_completed, juz_to_memorize)
        
        return jsonify(plan)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/islamic_chat', methods=['POST'])
def islamic_chat():
    try:
        data = request.json
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Please ask a question'}), 400
            
        if len(question) > 500:
            return jsonify({'error': 'Question too long. Please keep it under 500 characters.'}), 400
        
        # Get response from Islamic knowledge bot
        answer = islamic_bot.get_response(question)
        
        return jsonify({
            'question': question,
            'answer': answer,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
