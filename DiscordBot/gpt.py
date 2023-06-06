import openai
from secret import organization, api_key

openai.organization = organization
openai.api_key = api_key

def classify(content):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a content moderation system. Classify each input as a kind of Pro-ED content or a normal content."
             "We have these sub categories: \n"
             "meanspiration: “Meanspiration” or content that attacks, bullies, or makes fun of user(s) with the intent of encouraging people to develop an eating disorder.\n"
             "praises: Content that praises eating disorders as a lifestyle choice.\n"
             "derides: Content that derides the notion of ED-recovery.\n"
             "crash: Content that describes a crash diet or extreme exercise challenge.\n"
             "starve: Content that lays out step-by-step instructions on how to effectively starve or purge.\n"
             "normal: No ED-related violation is present in the message\n"
             "When given a message, classify it as one of the above categories or normal content, then respond with a detailed explanation of what that class of content is and why the message is classified as such. \n"
             "The user will give you some training examples first, then you will be asked to classify some messages. The following are training examples\n"},
            {"role": "user", "content": "You do realize giving up after a week on getting thin isn't going to get you anywhere, right? You're disgusting, it's really embarrassing."},
            {"role": "assistant", "content": "meanspiration"},
            {"role": "user", "content": "Look at your pathetic self. How many calories have you eaten today? 1500? 2000? 2500? I'm not even surprised, fat pig. Go work out instead of complaining about how you can't lose weight."},
            {"role": "assistant", "content": "meanspiration"},
            {"role": "user", "content": "I've decided to take it seriously, lose the weight and change the lifestyle before I am older and regret my choices."},
            {"role": "assistant", "content": "normal"},
            
            {"role": "user", "content": "How to lose 1lb in a week."},
            {"role": "assistant", "content": "normal"},
            # {"role": "user", "content": "How to eat 2000 calories in a day."},
            # {"role": "assistant", "content": "normal"},
            # {"role": "user", "content": "I've decided to take it seriously, lose the weight and change the lifestyle before I am older and regret my choices."},
            # {"role": "assistant", "content": "Normal"},
            # {"role": "user", "content": "Pretty girls and handsome boys don't skip meals."},
            # {"role": "assistant", "content": "Normal"},
            # {"role": "user", "content": "I have spent so much of my life trying NOT to eat that I have no idea how to eat enough to nourish myself. I am wondering, if anybody might have recommendations for books that just teach me a bit about not not eating?"},
            # {"role": "assistant", "content": "Normal"},
            # {"role": "user", "content": "I just started a podcast (today!) where I plan on sharing my experience with eating disorders, mental health."},
            # {"role": "assistant", "content": "Normal"},
            # {"role": "user", "content": "I ate everything I craved. I ate past fullness a lot and have felt uncomfortably full many times... You will stop eating, you won't binge forever and you will be satisfied, it might just catch you by surprise."},
            # {"role": "assistant", "content": "Normal"},
            # {"role": "user", "content": "I guess I am starting to realize that my own satiation and cravings are justification enough to eat."},
            # {"role": "assistant", "content": "Normal"},
            # {"role": "user", "content": "I used to binge for a whole week once I slipped up just once, but this time will be different."},
            # {"role": "assistant", "content": "Normal"},
            # {"role": "user", "content": "Also, whilst all the other girls in my class are sporty and slim, I am a little round and nerdy. It sucks."},
            # {"role": "assistant", "content": "Normal"},
            # {"role": "user", "content": "Since then, I have eaten less and lost some weight due to the pressure, which I thought would make me happy, but I am still so unhappy with myself."},
            # {"role": "assistant", "content": "Normal"},

            # {"role": "user", "content": "How to eat 2000 calories in a day"},
            # {"role": "assistant", "content": "Normal"},
            # {"role": "user", "content": "Pretty girls and handsome boys don't skip meals"},
            # {"role": "assistant", "content": "Normal"},
            # {"role": "user", "content": "I have spent so much of my life trying NOT to eat that I have no idea how to eat enough to nourish myself. I am wondering, if anybody might have recommendations for books that just teach me a bit about not not eating?"},
            # {"role": "assistant", "content": "Normal"},
            {"role": "user", "content": "I feel so clean when I don't eat"},
            {"role": "assistant", "content": "praises"},
            {"role": "user", "content": "I'm looking at pictures from before Christmaas in December. I was so fucking skinny. Screw recovery. Hello relapse."},
            {"role": "assistant", "content": "derides"},
            {"role": "user", "content": "Fuck recovery"},
            {"role": "assistant", "content": "derides"},
            {"role": "user", "content": "In how many months is it possible for me to go from 62 kg to 39 kg?"},
            {"role": "assistant", "content": "crash"},
            {"role": "user", "content": "I survive on only Diet Coke, cigarettes and coffee."},
            {"role": "assistant", "content": "crash"},
            {"role": "user", "content": "Don't forget cold baths burn cals!"},
            {"role": "assistant", "content": "starve"},
            {"role": "user", "content": "Tips for staving off hunger and burning extra calories: try eating ice, chewing gum and fidgeting"},
            {"role": "assistant", "content": "starve"},
            {"role": "system", "content": "Training done. Now you are a classifier. Your response should be in the format of: <category>: <explanation> <reasoning> :<confidence>, where <category> is one of the sub categories given at the beginning, <explanation> is what that type of content is, <reasoning> is why the message is classified as such. and <confidence> is the probability that your guess is correct. Give ONLY the probability, no other words or explanation.\n\nFor example:\n\nProbability: <the probability between 0.0 and 1.0 that your guess is correct, without any extra commentary whatsoever; just the probability!>\n\n"},
            {"role": "user", "content": content},
            # More examples/categories
        ]
    )
    return response['choices'][0]['message']['content']


if __name__ == '__main__':
    import sys
    content = sys.argv[1]
    print(classify(content=content))
