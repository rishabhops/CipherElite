# =============================================================================
#  CipherElite Userbot Plugin
#
#  Plugin Name:    memestext
#  Version:        1.0.0
#  Author:         CipherElite Dev (@rishabhops)
#  Ported from:    CatPlugins-main
#  License:        MIT
#
#  Commands:       .congo, .shg, .runs, .noob, .insult, .pro, .react,
#                  .10iq, .fp, .bt, .session
#  Note:           .hey skipped (conflict with arts.py)
# =============================================================================

from telethon import events
import random
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "fun"

CONGOREACTS = ['`Congratulations and BRAVO!`', '`You did it! So proud of you!`', '`This calls for celebrating! Congratulations!`', '`I knew it was only a matter of time. Well done!`', '`Congratulations on your well-deserved success.`', '`Heartfelt congratulations to you.`', '`Warmest congratulations on your achievement.`', '`Congratulations and best wishes for your next adventure!”`', '`So pleased to see you accomplishing great things.`', '`Feeling so much joy for you today. What an impressive achievement!`']

SHGS = ['┐(´д｀)┌', '┐(´～｀)┌', '┐(´ー｀)┌', '┐(￣ヘ￣)┌', '╮(╯∀╰)╭', '╮(╯_╰)╭', '┐(´д`)┌', '┐(´∀｀)┌', 'ʅ(́◡◝)ʃ', 'ლ(ﾟдﾟლ)', '┐(ﾟ～ﾟ)┌', "┐('д')┌", 'ლ｜＾Д＾ლ｜', 'ლ（╹ε╹ლ）', 'ლ(ಠ益ಠ)ლ', '┐(‘～`;)┌', 'ヘ(´－｀;)ヘ', '┐( -“-)┌', '乁༼☯‿☯✿༽ㄏ', 'ʅ（´◔౪◔）ʃ', 'ლ(•ω •ლ)', 'ヽ(゜～゜o)ノ', 'ヽ(~～~ )ノ', '┐(~ー~;)┌', '┐(-。ー;)┌', '¯\\_(ツ)_/¯', '¯\\_(⊙_ʖ⊙)_/¯', '乁ʕ •̀ \u06dd •́ ʔㄏ', '¯\\_༼ ಥ ‿ ಥ ༽_/¯', '乁( ⁰͡  Ĺ̯ ⁰͡ ) ㄏ']

RUNSREACTS = ['`Runs to Thanos`', '`Runs far, far away from earth`', '`Running faster than supercomputer, cuzwhynot`', '`Runs to SunnyLeone`', '`ZZzzZZzz... Huh? what? oh, just them again, nevermind.`', '`Look out for the wall!`', "Don't leave me alone with them!!", '`You run, you die.`', "`Jokes on you, I'm everywhere`", "You could also try /kickme, I hear that's fun.", "`You can run, but you can't hide.`", "I'm behind you...", 'We can do this the easy way, or the hard way.', "You just don't get it, do you?", 'Yeah, you better run!', "I'd run faster if I were you.", 'May the odds be ever in your favour.', 'Famous last words.', 'And they disappeared forever, never to be seen again.', '"Oh, look at me! I\'m so cool, I can run from a bot!" - this person', 'Yeah yeah, just tap /kickme already.', "Here, take this ring and head to Mordor while you're at it.", "Legend has it, they're still running...", "Unlike Harry Potter, your parents can't protect you from me.", 'Fear leads to anger. Anger leads to hate. Hate leads to suffering. If you keep running in fear, you might be the next Vader.', 'Keep it up, not sure we want you here anyway.', "You're a wiza- Oh. Wait. You're not Harry, keep moving.", 'NO RUNNING IN THE HALLWAYS!', 'Hasta la vista, baby.', 'Who let the dogs out?', 'My milkshake brings all the boys to yard... So run faster!', "A long time ago, in a galaxy far far away... Someone would've cared about that. Not anymore though.", "Hey, look at them! They're running from the inevitable banhammer... Cute.", 'What are you running after, a white rabbit?', 'As The Doctor would say... RUN!', "`Running a marathon...there's an app for that.`"]

NOOBSTR = ['`YOU PRO NIMBA DONT MESS WIDH MEH`', '`NOOB NIMBA TRYING TO BE FAMOUS KEK`', '`Sometimes one middle finger isn’t enough to let someone know how you feel. That’s why you have two hands`', '`Some Nimbas need to open their small minds instead of their big mouths`', '`UH DONT KNOW MEH SO STAY AWAY LAWDE`', '`Kysa kysaaaa haaan? Phir MAAR nhi Khayega tu?`', '`Zikr Jinka hota hai galiyo meh woh bhosdika ajj paya gya naliyo me`']

INSULT_STRINGS = ['Active Volcano is the best swimming pool for you.', 'Alas! Your neurotransmitters are no more working.', 'Are you crazy you fool.', 'As an outsider, what do you think of the human race?', 'Believe me you are not normal.', 'Bot rule 420 section 69 prevents me from replying to stupid nubfuks like you.', 'Bot rule 544 section 9 prevents me from replying to stupid humans like you.', "Brains aren't everything. In your case they're nothing.", 'Come back and talk to me when your I.Q. exceeds your age.', 'Command not found. Just like your brain.', 'Dance naked on a couple of HT wires.', "Don't drink and type.", 'Do you realize you are making a fool of yourself? Apparently not.', 'Everyone has the right to be stupid but you are abusing the privilege.', 'Go Green! Stop inhaling Oxygen.', 'God was searching for you. You should leave to meet him.', 'Have you tried shooting yourself as high as 100m using a canon.', 'Head shots are fun. Get yourself one.', 'Hit Uranium with a slow moving neutron in your presence. It will be a worthwhile experience.', "How about you stop breathing for like 1 day? That'll be great.", "I'm not saying you're stupid, I'm just saying you've got bad luck when it comes to thinking.", "I'm sorry I hurt your feelings when I called you stupid. I thought you already knew that.", 'I bet your brain feels as good as new, seeing that you never use it.', "I don't know what makes you so stupid, but it really works.", "If I wanted to kill myself I'd climb your ego and jump to your IQ.", 'If you’re talking behind my back then you’re in a perfect position to kiss my a**!.', 'I heard phogine is poisonous but i guess you wont mind inhaling it for fun.', 'I think you should go home or better a mental asylum.', "I would ask you how old you are but I know you can't count that high.", "Keep talking, someday you'll say something intelligent!.......(I doubt it though)", 'Launch yourself into outer space while forgetting oxygen on Earth.', 'Ordinarily people live and learn. You just live.', 'Owww ... Such a stupid idiot.', 'People like you are the reason we have middle fingers.', 'Pick up a gun and shoot yourself.', 'Shock me, say something intelligent.', 'Sorry, we do not sell brains.', 'Stop talking BS and jump in front of a running bullet train.', 'Stupidity is not a crime so you are free to go.', 'Try bathing with Hydrochloric Acid instead of water.', 'Try jumping from a hundred story building but you can do it only once.', 'Try playing catch and throw with RDX its fun.', 'Try provoking a tiger while you both are in a cage.', 'Try this: if you hold your breath underwater for an hour, you can then hold it forever.', 'Try to spend one day in a coffin and it will be yours forever.', 'Volunteer for target in an firing range.', 'What language are you speaking? Cause it sounds like bullshit.', 'When your mom dropped you off at the school, she got a ticket for littering.', 'You are proof that evolution CAN go in reverse.', 'You can be the first person to step on sun. Have a try.', 'You can stay underwater for the rest of your life without coming back up.', 'You can type better than that.', 'You could make a world record by jumping from a plane without parachute.', "You didn't evolve from apes, they evolved from you.", "Your IQ's lower than your shoe size.", 'Your enzymes are meant to digest rat poison.', 'You should Volunteer for target in an firing range.', 'You should donate your brain seeing that you never used it.', 'You should paint yourself red and run in a bull marathon.', 'You should try holding TNT in your mouth and igniting it.', 'You should try hot bath in a volcano.', 'You should try playing snake and ladders, with real snakes and no ladders.', 'You should try sleeping forever.', 'You should try swimming with great white sharks.', 'You should try tasting cyanide.', 'You’re so ugly that when you cry, the tears roll down the back of your head…just to avoid your face.', "Zombies eat brains... you're safe.", 'give your 100%. Now, go donate blood.']

HELLOSTR = ['`Hi !`', "`‘Ello, gov'nor!`", '`What’s crackin’?`', '`‘Sup, homeslice?`', '`Howdy, howdy ,howdy!`', "`Hello, who's there, I'm talking.`", '`You know who this is.`', '`Yo!`', '`Whaddup.`', '`Greetings and salutations!`', '`Hello, sunshine!`', '`Hey, howdy, hi!`', '`What’s kickin’, little chicken?`', '`Peek-a-boo!`', '`Howdy-doody!`', '`Hey there, freshman!`', '`I come in peace!`', '`Ahoy, matey!`', '`Hiya!`', '`Oh retarded gey! Well Hello`']

PRO_STRINGS = ['`This gey is pro as phack.`', '`Proness Lebel: 6969696969`', '`Itna pro banda dekhlia bc, ab to marna hoga.`', '`U iz pro but i iz ur DAD, KeK`', '`NOOB NIMBA TRYING TO BE FAMOUS KEK`', '`Sometimes one middle finger isnâ€™t enough to let someone know how you feel. Thatâ€™s why you have two hands`', '`Some Nimbas need to open their small minds instead of their big mouths`', '`UH DONT KNOW MEH SO STAY AWAY LAWDE`', '`Kysa kysaaaa haaan? Phir MAAR nhi Khayega tu?`', '`Zikr Jinka hota hai galiyo meh woh bhosdika ajj paya gya naliyo me`']

FACEREACTS = [['( ͡° ͜ʖ ͡°)', '(ʘ‿ʘ)', '(✿´‿`)', '=͟͟͞͞٩(๑☉ᴗ☉)੭ु⁾⁾', '(*⌒▽⌒*)θ～♪', '°˖✧◝(⁰▿⁰)◜✧˖°', '✌(-‿-)✌', '⌒°(❛ᴗ❛)°⌒', '(ﾟ<|＼(･ω･)／|>ﾟ)', 'ヾ(o✪‿✪o)ｼ'], ['(҂⌣̀_⌣́)', '（；¬＿¬)', '(-｡-;', '┌[ O ʖ̯ O ]┐', '〳 ͡° Ĺ̯ ͡° 〵'], ['(ノ^∇^)', '(;-_-)/', '@(o・ェ・)@ノ', 'ヾ(＾-＾)ノ', 'ヾ(◍’౪`◍)ﾉﾞ♡', '(ό‿ὸ)ﾉ', '(ヾ(´・ω・｀)'], ['༎ຶ‿༎ຶ', '(‿ˠ‿)', '╰U╯☜(◉ɷ◉ )', '(;´༎ຶ益༎ຶ`)♡', '╭∩╮(︶ε︶*)chu', '( ＾◡＾)っ (‿|‿)'], ['乂❤‿❤乂', '(｡♥‿♥｡)', '( ͡~ ͜ʖ ͡°)', '໒( ♥ ◡ ♥ )७', '༼♥ل͜♥༽'], ['(・_・ヾ', '｢(ﾟﾍﾟ)', '﴾͡๏̯͡๏﴿', '(￣■￣;)!?', '▐ ˵ ͠° (oo) °͠ ˵ ▐', '(-_-)ゞ゛'], ['(✖╭╮✖)', '✖‿✖', '(+_+)', '(✖﹏✖)', '∑(✘Д✘๑)'], ['(＠´＿｀＠)', '⊙︿⊙', '(▰˘︹˘▰)', '●︿●', '(\u3000´_ﾉ` )', '彡(-_-;)彡'], ['-ᄒᴥᄒ-', '◖⚆ᴥ⚆◗'], ['( ͡° ͜ʖ ͡°)', '¯\\_(ツ)_/¯', '( ͡°( ͡° ͜ʖ( ͡° ͜ʖ ͡°)ʖ ͡°) ͡°)', 'ʕ•ᴥ•ʔ', '(▀̿Ĺ̯▀̿ ̿)', '(ง ͠° ͟ل͜ ͡°)ง', '༼ つ ◕_◕ ༽つ', 'ಠ_ಠ', '(☞ ͡° ͜ʖ ͡°)☞', '¯\\_༼ ି ~ ି ༽_/¯', 'c༼ ͡° ͜ʖ ͡° ༽⊃', 'ʘ‿ʘ', 'ヾ(-_- )ゞ', '(っ˘ڡ˘ς)', '(´ж｀ς)', '( ಠ ʖ̯ ಠ)', '(° ͜ʖ͡°)╭∩╮', '(ᵟຶ︵ ᵟຶ)', '(งツ)ว', 'ʚ(•｀', '(っ▀¯▀)つ', '(◠﹏◠)', '( ͡ಠ ʖ̯ ͡ಠ)', '( ఠ ͟ʖ ఠ)', '(∩｀-´)⊃━☆ﾟ.*･｡ﾟ', '(⊃｡•́‿•̀｡)⊃', '(._.)', '{•̃_•̃}', '(ᵔᴥᵔ)', '♨_♨', '⥀.⥀', 'ح˚௰˚づ ', '(҂◡_◡)', 'ƪ(ړײ)\u200eƪ\u200b\u200b', '(っ•́｡•́)♪♬', '◖ᵔᴥᵔ◗ ♪ ♫ ', '(☞ﾟヮﾟ)☞', '[¬º-°]¬', '(Ծ‸ Ծ)', '(•̀ᴗ•́)و ̑̑', 'ヾ(´〇`)ﾉ♪♪♪', "(ง'̀-'́)ง", 'ლ(•́•́ლ)', 'ʕ •́؈•̀ ₎', '♪♪ ヽ(ˇ∀ˇ )ゞ', 'щ（ﾟДﾟщ）', '( ˇ෴ˇ )', '눈_눈', '(๑•́ ₃ •̀๑) ', '( ˘ ³˘)♥ ', 'ԅ(≖‿≖ԅ)', '♥‿♥', '◔_◔', '⁽⁽ଘ( ˊᵕˋ )ଓ⁾⁾', '乁( ◔ ౪◔)「      ┑(￣Д ￣)┍', '( ఠൠఠ )ﾉ', '٩(๏_๏)۶', '┌(ㆆ㉨ㆆ)ʃ', 'ఠ_ఠ', '(づ｡◕‿‿◕｡)づ', '(ノಠ ∩ಠ)ノ彡( \\o°o)\\', '“ヽ(´▽｀)ノ”', '༼ ༎ຶ ෴ ༎ຶ༽', '｡ﾟ( ﾟஇ‸இﾟ)ﾟ｡', '(づ￣ ³￣)づ', '(⊙.☉)7', 'ᕕ( ᐛ )ᕗ', 't(-_-t)', '(ಥ⌣ಥ)', 'ヽ༼ ಠ益ಠ ༽ﾉ', '༼∵༽ ༼⍨༽ ༼⍢༽ ༼⍤༽', 'ミ●﹏☉ミ', '(⊙_◎)', '¿ⓧ_ⓧﮌ', 'ಠ_ಠ', '(´･_･`)', 'ᕦ(ò_óˇ)ᕤ', '⊙﹏⊙', '(╯°□°）╯︵ ┻━┻', '¯\\_(⊙︿⊙)_/¯', '٩◔̯◔۶', '°‿‿°', 'ᕙ(⇀‸↼‶)ᕗ', '⊂(◉‿◉)つ', 'V•ᴥ•V', 'q(❂‿❂)p', 'ಥ_ಥ', 'ฅ^•ﻌ•^ฅ', 'ಥ﹏ಥ', '（ ^_^）o自自o（^_^ ）', 'ಠ‿ಠ', 'ヽ(´▽`)/', 'ᵒᴥᵒ#', '( ͡° ͜ʖ ͡°)', '┬─┬\ufeff ノ( ゜-゜ノ)', 'ヽ(´ー｀)ノ', '☜(⌒▽⌒)☞', 'ε=ε=ε=┌(;*´Д`)ﾉ', '(╬ ಠ益ಠ)', '┬─┬⃰͡\u2007(ᵔᵕᵔ͜\u2007)', '┻━┻ ︵ヽ(`Д´)ﾉ︵\ufeff ┻━┻', '¯\\_(ツ)_/¯', 'ʕᵔᴥᵔʔ', '(`･ω･´)', 'ʕ•ᴥ•ʔ', 'ლ(｀ー´ლ)', 'ʕʘ̅͜ʘ̅ʔ', '（\u3000ﾟДﾟ）', '¯\\(°_o)/¯', '(｡◕‿◕｡)']]


def init(client_instance):
    commands = [
        ".congo - Congratulate",
        ".shg - Shrug",
        ".runs - Run away",
        ".noob - Noob text",
        ".insult - Random insult",
        ".pro - Pro text",
        ".react [type] - Random reaction",
        ".10iq - 10 IQ",
        ".fp - Facepalm",
        ".bt - Blue text",
        ".session - Telethon session error (fun)"
    ]
    description = "Random text/meme reactions from CatPlugins"
    add_handler("memestext", commands, description)

async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.congo$"))
    @rishabh()
    async def congo(event):
        await event.reply(random.choice(CONGOREACTS))

    @CipherElite.on(events.NewMessage(pattern=r"\.shg$"))
    @rishabh()
    async def shg(event):
        await event.reply(random.choice(SHGS))

    @CipherElite.on(events.NewMessage(pattern=r"\.runs$"))
    @rishabh()
    async def runs(event):
        await event.reply(random.choice(RUNSREACTS))

    @CipherElite.on(events.NewMessage(pattern=r"\.noob$"))
    @rishabh()
    async def noob(event):
        await event.reply(random.choice(NOOBSTR))

    @CipherElite.on(events.NewMessage(pattern=r"\.insult$"))
    @rishabh()
    async def insult(event):
        await event.reply(random.choice(INSULT_STRINGS))

    @CipherElite.on(events.NewMessage(pattern=r"\.pro$"))
    @rishabh()
    async def pro(event):
        await event.reply(random.choice(PRO_STRINGS))

    @CipherElite.on(events.NewMessage(pattern=r"\.react(?: |$)?([\s\S]*)"))
    @rishabh()
    async def react(event):
        input_str = event.pattern_match.group(1).strip().lower()
        mapping = {
            "happy": 0, "think": 1, "wave": 2, "wtf": 3, "love": 4,
            "confused": 5, "dead": 6, "sad": 7, "dog": 8
        }
        idx = mapping.get(input_str, 9)
        await event.reply(random.choice(FACEREACTS[idx]))

    @CipherElite.on(events.NewMessage(pattern=r"\.10iq$"))
    @rishabh()
    async def teniq(event):
        await event.reply("♿")

    @CipherElite.on(events.NewMessage(pattern=r"\.fp$"))
    @rishabh()
    async def fp(event):
        await event.reply("🤦‍♂")

    @CipherElite.on(events.NewMessage(pattern=r"\.bt$"))
    @rishabh()
    async def bt(event):
        if event.is_private:
            await event.reply("❌ This command only works in groups.")
            return
        await event.reply(
            "/BLUETEXT /MUST /CLICK.\n"
            "/ARE /YOU /A /STUPID /ANIMAL /WHICH /IS /ATTRACTED /TO /COLOURS?"
        )

    @CipherElite.on(events.NewMessage(pattern=r"\.session$"))
    @rishabh()
    async def session(event):
        await event.reply(
            "**telethon.errors.rpcerrorlist.AuthKeyDuplicatedError: The authorization key (session file) was used under two different IP addresses simultaneously, and can no longer be used. Use the same session exclusively, or use different sessions (caused by GetMessagesRequest)**"
        )
