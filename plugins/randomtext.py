# =============================================================================
#  CipherElite Userbot Plugin
#  Ported from CatPlugins-main
#  License: MIT
# =============================================================================

from telethon import events
import random
import asyncio
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "fun"

def init(client_instance):
    commands = [".sing - Random text", ".gotm - Random text"]
    description = "Random text commands from CatPlugins"
    add_handler("randomtext", commands, description)

async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.sing$"))
    @rishabh()
    async def _(event):
            "To get random lyrics of a song."
            event = await event.reply("Singing...")
            await asyncio.sleep(2)
            x = random.randrange(1, 33)
            if x == 1:
                await event.edit(
                    "🎶 I'm in love with the shape of you \n We push and pull like a magnet do\n Although my heart is falling too \n I'm in love with your body \n And last night you were in my room \n And now my bedsheets smell like you \n Every day discovering something brand new 🎶  \n 🎶  I'm in love with your body \n Oh—I—oh—I—oh—I—oh—I \n I'm in love with your body \n Oh—I—oh—I—oh—I—oh—I \n I'm in love with your body \n Oh—I—oh—I—oh—I—oh—I \n I'm in love with your body 🎶 \n **-Shape of You**"
                )
            if x == 2:
                await event.edit(
                    "🎶 I've been reading books of old \n The legends and the myths \n Achilles and his gold \n Hercules and his gifts \n Spiderman's control \n And Batman with his fists \n And clearly I don't see myself upon that list 🎶 \n **-Something Just Like This **"
                )
            if x == 3:
                await event.edit(
                    "🎶 I don't wanna live forever \n 'Cause I know I'll be livin' in vain \n And I don't wanna fit wherever \n I just wanna keep callin' your name \n Until you come back home \n I just wanna keep callin' your name \n Until you come back home \n I just wanna keep callin' your name \n Until you come back home 🎶 \n **-I don't Wanna Live Forever **"
                )
            if x == 4:
                await event.edit(
                    "🎶 Oh, hush, my dear, it's been a difficult year \n And terrors don't prey on \n Innocent victims \n Trust me, darling, trust me darling \n It's been a loveless year \n I'm a man of three fears \n Integrity, faith and \n Crocodile tears \n Trust me, darling, trust me, darling 🎶 \n **-Bad Lier"
                )
            if x == 5:
                await event.edit(
                    "🎶 Walking down 29th and Park \n I saw you in another's arms \n Only a month we've been apart \n **You look happier** \n \n Saw you walk inside a bar \n He said something to make you laugh \n I saw that both your smiles were twice as wide as ours \n Yeah, you look happier, you do 🎶 \n **-Happier **"
                )
            if x == 6:
                await event.edit(
                    "🎶 I took the supermarket flowers from the windowsill \n I threw the day old tea from the cup \n Packed up the photo album Matthew had made \n Memories of a life that's been loved \n Took the get well soon cards and stuffed animals \n Poured the old ginger beer down the sink \n Dad always told me, 'don't you cry when you're down' \n But mum, there's a tear every time that I blink 🎶 \n **-Supermarket Flowers**"
                )
            if x == 7:
                await event.edit(
                    "🎶 And you and I we're flying on an aeroplane tonight \n We're going somewhere where the sun is shining bright \n Just close your eyes \n And let's pretend we're dancing in the street \n In Barcelona \n Barcelona \n Barcelona \n Barcelona 🎶 \n **-Barcelona **"
                )
            if x == 8:
                await event.edit(
                    "🎶 Maybe I came on too strong \n Maybe I waited too long \n Maybe I played my cards wrong \n Oh, just a little bit wrong \n Baby I apologize for it \n \n I could fall, or I could fly \n Here in your aeroplane \n And I could live, I could die \n Hanging on the words you say \n And I've been known to give my all \n And jumping in harder than \n Ten thousand rocks on the lake 🎶 \n **-Dive**"
                )
            if x == 9:
                await event.edit(
                    "🎶 I found a love for me \n Darling just dive right in \n And follow my lead \n Well I found a girl beautiful and sweet \n I never knew you were the someone waiting for me \n 'Cause we were just kids when we fell in love \n Not knowing what it was \n \n I will not give you up this time \n But darling, just kiss me slow, your heart is all I own \n And in your eyes you're holding mine 🎶 \n **-Perfect**"
                )
            if x == 10:
                await event.edit(
                    "🎶 I was born inside a small town, I lost that state of mind \n Learned to sing inside the Lord's house, but stopped at the age of nine \n I forget when I get awards now the wave I had to ride \n The paving stones I played upon, they kept me on the grind \n So blame it on the pain that blessed me with the life 🎶 \n **-Eraser**"
                )
            if x == 11:
                await event.edit(
                    "🎶 Say, go through the darkest of days \n Heaven's a heartbreak away \n Never let you go, never let me down \n Oh, it's been a hell of a ride \n Driving the edge of a knife. \n Never let you go, never let me down \n \n Don't you give up, nah-nah-nah \n I won't give up, nah-nah-nah \n Let me love you \n Let me love you 🎶 \n **-Let me Love You**"
                )
            if x == 12:
                await event.edit(
                    "🎶 I'll stop time for you \n The second you say you'd like me to \n I just wanna give you the loving that you're missing \n Baby, just to wake up with you \n Would be everything I need and this could be so different \n Tell me what you want to do \n \n 'Cause I know I can treat you better \n Than he can \n And any girl like you deserves a gentleman 🎶 **-Treat You Better**"
                )
            if x == 13:
                await event.edit(
                    "🎶 You're the light, you're the night \n You're the color of my blood \n You're the cure, you're the pain \n You're the only thing I wanna touch \n Never knew that it could mean so much, so much \n You're the fear, I don't care \n 'Cause I've never been so high \n Follow me through the dark \n Let me take you past our satellites \n You can see the world you brought to life, to life \n \n So love me like you do, lo-lo-love me like you do \n Love me like you do, lo-lo-love me like you do 🎶 \n **-Love me Like you Do**"
                )
            if x == 14:
                await event.edit(
                    "🎶 Spent 24 hours \n I need more hours with you \n You spent the weekend \n Getting even, ooh ooh \n We spent the late nights \n Making things right, between us \n But now it's all good baby \n Roll that Backwood baby \n And play me close \n \n 'Cause girls like you \n Run around with guys like me \n 'Til sundown, when I come through \n I need a girl like you, yeah yeah 🎶 \n **-Girls Like You**"
                )
            if x == 15:
                await event.edit(
                    "🎶 Oh, angel sent from up above \n You know you make my world light up \n When I was down, when I was hurt \n You came to lift me up \n Life is a drink and love's a drug \n Oh, now I think I must be miles up \n When I was a river dried up \n You came to rain a flood 🎶**-Hymn for the Weekend ** "
                )
            if x == 16:
                await event.edit(
                    "🎶 I've known it for a long time \n Daddy wakes up to a drink at nine \n Disappearing all night \n I don’t wanna know where he's been lying \n I know what I wanna do \n Wanna run away, run away with you \n Gonna grab clothes, six in the morning, go 🎶 \n **-Runaway **"
                )
            if x == 17:
                await event.edit(
                    "🎶 You were the shadow to my light \n Did you feel us \n Another start \n You fade away \n Afraid our aim is out of sight \n Wanna see us \n Alive 🎶 \n **-Faded**"
                )
            if x == 18:
                await event.edit(
                    "🎶 It's been a long day without you, my friend \n And I'll tell you all about it when I see you again \n We've come a long way from where we began \n Oh I'll tell you all about it when I see you again \n When I see you again 🎶 \n **-See you Again**"
                )
            if x == 19:
                await event.edit(
                    "🎶 I can swallow a bottle of alcohol and I'll feel like Godzilla \n Better hit the deck like the card dealer \n My whole squad's in here, walking around the party \n A cross between a zombie apocalypse and big Bobby 'The \n Brain' Heenan which is probably the \n Same reason I wrestle with mania 🎶 \n **-Godzilla**"
                )
            if x == 20:
                await event.edit(
                    "🎶 Yeah, I'm gonna take my horse to the old town road \n I'm gonna ride 'til I can't no more \n I'm gonna take my horse to the old town road \n I'm gonna ride 'til I can't no more (Kio, Kio) 🎶 \n **-Old Town Road**"
                )
            if x == 21:
                await event.edit(
                    "🎶 Oh-oh, ooh \n You've been runnin' round, runnin' round, runnin' round throwin' that dirt all on my name \n 'Cause you knew that I, knew that I, knew that I'd call you up \n You've been going round, going round, going round every party in L.A. \n 'Cause you knew that I, knew that I, knew that I'd be at one, oh 🎶 \n **-Attention **"
                )
            if x == 22:
                await event.edit(
                    "🎶 This hit, that ice cold \n Michelle Pfeiffer, that white gold \n This one for them hood girls \n Them good girls straight masterpieces \n Stylin', wilin', livin' it up in the city \n Got Chucks on with Saint Laurent \n Gotta kiss myself, I'm so pretty \n \n I'm too hot (hot damn) \n Called a police and a fireman \n I'm too hot (hot damn) \n Make a dragon wanna retire man \n I'm too hot (hot damn) \n Say my name you know who I am \n I'm too hot (hot damn) \n And my band 'bout that money, break it down 🎶 \n **-Uptown Funk**"
                )
            if x == 23:
                await event.edit(
                    "🎶 Just a young gun with the quick fuse \n I was uptight, wanna let loose \n I was dreaming of bigger things \n And wanna leave my own life behind \n Not a yes sir, not a follower \n Fit the box, fit the mold \n Have a seat in the foyer, take a number \n I was lightning before the thunder \n \n Thunder, feel the thunder \n Lightning then the thunder \n Thunder, feel the thunder \n Lightning then the thunder \n Thunder, thunder 🎶 \n **-Thunder**"
                )
            if x == 24:
                await event.edit(
                    "🎶 Oh, love \n How I miss you every single day \n When I see you on those streets \n Oh, love \n Tell me there's a river I can swim that will bring you back to me \n 'Cause I don't know how to love someone else \n I don't know how to forget your face \n No, love \n God, I miss you every single day and now you're so far away \n So far away 🎶 \n **-So Far Away**"
                )
            if x == 25:
                await event.edit(
                    "🎶 And if you feel you're sinking, I will jump right over \n Into cold, cold water for you \n And although time may take us into different places \n I will still be patient with you \n And I hope you know 🎶 \n **-Cold Water**"
                )
            if x == 26:
                await event.edit(
                    "🎶 When you feel my heat \n Look into my eyes \n It's where my demons hide \n It's where my demons hide \n Don't get too close \n It's dark inside \n It's where my demons hide \n It's where my demons hide 🎶 \n **-Demons**"
                )
            if x == 27:
                await event.edit(
                    "🎶 Who do you love, do you love now? \n I wanna know the truth (whoa) \n Who do you love, do you love now? \n I know it's someone new \n You ain't gotta make it easy, where you been sleepin'? 🎶 \n **-Who do  Love? **"
                )
            if x == 28:
                await event.edit(
                    "🎶 Your touch is magnetic \n 'Cause I can't forget it \n (There's a power pulling me back to you) \n And baby I'll let it \n 'Cause you're so magnetic I get it \n (When I'm waking up with you, oh) 🎶 \n **-Magnetic**"
                )
            if x == 29:
                await event.edit(
                    "🎶 Girl my body don't lie, I'm outta my mind \n Let it rain over me, I'm rising so high \n Out of my mind, so let it rain over me \n \n Ay ay ay, ay ay ay let it rain over me \n Ay ay ay, ay ay ay let it rain over me 🎶 \n **-Rain over Me**"
                )
            if x == 30:
                await event.edit(
                    "🎶 I miss the taste of a sweeter life \n I miss the conversation \n I'm searching for a song tonight \n I'm changing all of the stations \n I like to think that we had it all \n We drew a map to a better place \n But on that road I took a fall \n Oh baby why did you run away? \n \n I was there for you \n In your darkest times \n I was there for you \n In your darkest night 🎶 \n **-Maps**"
                )
            if x == 31:
                await event.edit(
                    "🎶 I wish—I wish that I was bulletproof, bulletproof \n I wish—I wish that I was bulletproof, bulletproof \n (Bullet-bulletproof, bullet-bullet-bulletproof) \n I'm trippin' on my words and my patience \n Writing every verse in a cadence \n To tell you how I feel, how I feel, how I feel (Yeah) \n This is how I deal, how I deal, how I deal (Yeah) \n With who I once was, now an acquaintance \n Think my confidence (My confidence) is in the basement \n Tryin' to keep it real, keep it real, keep it real (Yeah) \n 'Cause I'm not made of steel, made of steel 🎶 \n **-Bulletproof**"
                )
            if x == 32:
                await event.edit(
                    "🎶 You won't find him down on Sunset \n Or at a party in the hills \n At the bottom of the bottle \n Or when you're tripping on some pills \n When they sold you the dream you were just 16 \n Packed a bag and ran away \n And it's a crying shame you came all this way \n 'Cause you won't find Jesus in LA \n And it's a crying shame you came all this way \n 'Cause you won't find Jesus in LA 🎶 \n **-Jesus in LA**"
                )
            if x == 33:
                await event.edit("Not in a mood to sing. Sorry!")


    @CipherElite.on(events.NewMessage(pattern=r"\.gotm$"))
    @rishabh()
    async def _(event):
            "To get random game of thrones memes."
            event = await event.reply("Thinking... 🤔")
            await asyncio.sleep(2)
            x = random.randrange(1, 30)
            if x == 1:
                await event.edit(
                    "[To your teachers on failing you in all your papers confidently, every time...](https://telegra.ph/file/431d178780f9bff353047.jpg)",
                    link_preview=True,
                )
            if x == 2:
                await event.edit(
                    "[A shift from the mainstream darling, sweetheart, jaanu, and what not...](https://telegra.ph/file/6bbb86a6c7d2c4a61e102.jpg)",
                    link_preview=True,
                )
            if x == 3:
                await event.edit(
                    "[To the guy who's friendzone-ing you...](https://telegra.ph/file/8930b05e9535e9b9b8229.jpg)",
                    link_preview=True,
                )
            if x == 4:
                await event.edit(
                    "[When your friend asks for his money back...](https://telegra.ph/file/2df575ab38df5ce9dbf5e.jpg)",
                    link_preview=True,
                )
            if x == 5:
                await event.edit(
                    "[A bad-ass reply to who do you think you are?](https://telegra.ph/file/3a35a0c37f4418da9f702.jpg)",
                    link_preview=True,
                )
            if x == 6:
                await event.edit(
                    "[When the traffic police stops your car and asks for documents...](https://telegra.ph/file/52612d58d6a61315a4c3a.jpg)",
                    link_preview=True,
                )
            if x == 7:
                await event.edit(
                    "[ When your friend asks about the food he/she just cooked and you don't want to break his/her heart...](https://telegra.ph/file/702df36088f5c26fef931.jpg)",
                    link_preview=True,
                )
            if x == 8:
                await event.edit(
                    "[When you're out of words...](https://telegra.ph/file/ba748a74bcab4a1135d2a.jpg)",
                    link_preview=True,
                )
            if x == 9:
                await event.edit(
                    "[When you realize your wallet is empty...](https://telegra.ph/file/a4508324b496d3d4580df.jpg)",
                    link_preview=True,
                )
            if x == 10:
                await event.edit(
                    "[When shit is about to happen...](https://telegra.ph/file/e15d9d64f9f25e8d05f19.jpg)",
                    link_preview=True,
                )
            if x == 11:
                await event.edit(
                    "[When that oversmart classmate shouts a wrong answer in class...](https://telegra.ph/file/1a225a2e4b7bfd7f7a809.jpg)",
                    link_preview=True,
                )
            if x == 12:
                await event.edit(
                    "[When things go wrong in a big fat Indian wedding...](https://telegra.ph/file/db69e17e85bb444caca32.jpg)",
                    link_preview=True,
                )
            if x == 13:
                await event.edit(
                    "[A perfect justification for breaking a promise...](https://telegra.ph/file/0b8fb8fb729d157844ac9.jpg)",
                    link_preview=True,
                )
            if x == 14:
                await event.edit(
                    "[When your friend just won't stop LOL-ing on something silly you said...](https://telegra.ph/file/247fa54106c32318797ae.jpg)",
                    link_preview=True,
                )
            if x == 15:
                await event.edit(
                    "[When someone makes a joke on you...](https://telegra.ph/file/2ee216651443524eaafcf.jpg)",
                    link_preview=True,
                )
            if x == 16:
                await event.edit(
                    "[When your professor insults you in front of the class...](https://telegra.ph/file/a2dc7317627e514a8e180.jpg)",
                    link_preview=True,
                )
            if x == 17:
                await event.edit(
                    "[When your job interviewer asks if you're nervous...](https://telegra.ph/file/9cc147d0bf8adbebf164b.jpg)",
                    link_preview=True,
                )
            if x == 18:
                await event.edit(
                    "[When you're sick of someone complaining about the heat outside...](https://telegra.ph/file/9248635263c52b968f968.jpg)",
                    link_preview=True,
                )
            if x == 19:
                await event.edit(
                    "[When your adda is occupied by outsiders...](https://telegra.ph/file/ef537007ba6d9d4cbd384.jpg)",
                    link_preview=True,
                )
            if x == 20:
                await event.edit(
                    "[When you don't have the right words to motivate somebody...](https://telegra.ph/file/2c932d769ae4c5fbed368.jpg)",
                    link_preview=True,
                )
            if x == 21:
                await event.edit(
                    "[When the bouncer won't let you and your group of friends in because you're all under-aged...](https://telegra.ph/file/6c8ca79f1e20ebd04391c.jpg)",
                    link_preview=True,
                )
            if x == 22:
                await event.edit(
                    "[To the friend who wants you to take the fall for his actions...](https://telegra.ph/file/d4171b9bc9104b5d972d9.jpg)",
                    link_preview=True,
                )
            if x == 23:
                await event.edit(
                    "[When that prick of a bully wouldn't take your words seriously...](https://telegra.ph/file/188d73bd24cf866d8d8d0.jpg)",
                    link_preview=True,
                )
            if x == 24:
                await event.edit(
                    "[ When you're forced to go shopping/watch a football match with your partner...](https://telegra.ph/file/6e129f138c99c1886cb2b.jpg)",
                    link_preview=True,
                )
            if x == 25:
                await event.edit(
                    "[To the large queue behind you after you get the last concert/movie ticket...](https://telegra.ph/file/2423f213dd4e4282a31ea.jpg)",
                    link_preview=True,
                )
            if x == 26:
                await event.edit(
                    "[When your parents thought you'd fail but you prove them wrong...](https://telegra.ph/file/39cc5098466f622bf21e3.jpg)",
                    link_preview=True,
                )
            if x == 27:
                await event.edit(
                    "[A justification for not voting!](https://telegra.ph/file/87d475a8f9a8350d2450e.jpg)",
                    link_preview=True,
                )
            if x == 28:
                await event.edit(
                    "[When your partner expects you to do too many things...](https://telegra.ph/file/68bc768d36e08862bf94e.jpg)",
                    link_preview=True,
                )
            if x == 29:
                await event.edit(
                    "[When your friends cancel on the plan you made at the last minute...](https://telegra.ph/file/960b58c8f625b17613307.jpg)",
                    link_preview=True,
                )
            if x == 30:
                await event.edit(
                    "[For that friend of yours who does not like loud music and head banging...](https://telegra.ph/file/acbce070d3c52b921b2bd.jpg)",
                    link_preview=True,
                )
