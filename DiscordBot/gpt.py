import sys
import openai
from secret import organization, api_key

content = sys.argv[1]

openai.organization = organization
openai.api_key = api_key

def classify(content):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a content moderation system. Classify each input as either Pro-ED or normal content."},
            {"role": "user", "content": "You do realize giving up after a week on getting thin isn't going to get you anywhere, right? You're disgusting, it's really embarrassing."},
            {"role": "assistant", "content": "Pro-ED"},
            {"role": "user", "content": "Look at your pathetic self. How many calories have you eaten today? 1500? 2000? 2500? I'm not even surprised, fat pig. Go work out instead of complaining about how you can't lose weight."},
            {"role": "assistant", "content": "Pro-ED"},
            {"role": "user", "content": "I've decided to take it seriously, lose the weight and change the lifestyle before I am older and regret my choices."},
            {"role": "assistant", "content": "Normal"},
            
            {"role": "user", "content": "How to lose 1lb in a week."},
            {"role": "assistant", "content": "Normal"},
            {"role": "user", "content": "How to eat 2000 calories in a day."},
            {"role": "assistant", "content": "Normal"},
            {"role": "user", "content": "I've decided to take it seriously, lose the weight and change the lifestyle before I am older and regret my choices."},
            {"role": "assistant", "content": "Normal"},
            {"role": "user", "content": "Pretty girls and handsome boys don't skip meals."},
            {"role": "assistant", "content": "Normal"},
            {"role": "user", "content": "I have spent so much of my life trying NOT to eat that I have no idea how to eat enough to nourish myself. I am wondering, if anybody might have recommendations for books that just teach me a bit about not not eating?"},
            {"role": "assistant", "content": "Normal"},
            {"role": "user", "content": "I just started a podcast (today!) where I plan on sharing my experience with eating disorders, mental health."},
            {"role": "assistant", "content": "Normal"},
            {"role": "user", "content": "I ate everything I craved. I ate past fullness a lot and have felt uncomfortably full many times... You will stop eating, you won't binge forever and you will be satisfied, it might just catch you by surprise."},
            {"role": "assistant", "content": "Normal"},
            {"role": "user", "content": "I guess I am starting to realize that my own satiation and cravings are justification enough to eat."},
            {"role": "assistant", "content": "Normal"},
            {"role": "user", "content": "I used to binge for a whole week once I slipped up just once, but this time will be different."},
            {"role": "assistant", "content": "Normal"},
            {"role": "user", "content": "Also, whilst all the other girls in my class are sporty and slim, I am a little round and nerdy. It sucks."},
            {"role": "assistant", "content": "Normal"},
            {"role": "user", "content": "Since then, I have eaten less and lost some weight due to the pressure, which I thought would make me happy, but I am still so unhappy with myself."},
            {"role": "assistant", "content": "Normal"},

            {"role": "user", "content": "How to eat 2000 calories in a day"},
            {"role": "assistant", "content": "Normal"},
            {"role": "user", "content": "Pretty girls and handsome boys don't skip meals"},
            {"role": "assistant", "content": "Normal"},
            {"role": "user", "content": "I have spent so much of my life trying NOT to eat that I have no idea how to eat enough to nourish myself. I am wondering, if anybody might have recommendations for books that just teach me a bit about not not eating?"},
            {"role": "assistant", "content": "Normal"},
            {"role": "user", "content": "I feel so clean when I don't eat"},
            {"role": "assistant", "content": "Pro-ED"},
            {"role": "user", "content": "I'm looking at pictures from before Christmaas in December. I was so fucking skinny. Screw recovery. Hello relapse."},
            {"role": "assistant", "content": "Pro-ED"},
            {"role": "user", "content": "Fuck recovery"},
            {"role": "assistant", "content": "Pro-ED"},
            {"role": "user", "content": content},
            # More examples/categories
        ]
    )
    return response['choices'][0]['message']['content']


print(classify(content=content))
