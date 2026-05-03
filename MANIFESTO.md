# Artist's Manifesto
## *Echoes Through the Door: A Threshold of Voices*

---

### Preface

Bob Dylan wrote "Knockin' on Heaven's Door" in the summer of 1973 for a dying sheriff in Sam Peckinpah's *Pat Garrett and Billy the Kid*. The scene lasts barely two minutes: a man lies in the dust, his wife kneeling beside him, and somewhere in that silence between living and not-living, the song begins. It is not a protest song. It is not even, strictly speaking, a war song. It is a song about the exact moment when a person realizes they have carried something as far as they can carry it.

That moment — that precise threshold — became the center of everything we built.

---

### I. Why This Medium: The Conversation as the Only Honest Form

When we first began thinking about how to engage with 1973, we considered several possible forms. A visual essay tracing the war through archival imagery. A generative soundscape built from the harmonic structure of the song itself. A data visualization mapping anti-war sentiment across the decade.

We set them all aside. None of them answered the question we kept returning to: *How do you actually understand what someone felt in that moment?*

You cannot understand it by looking at a photograph. Photographs flatten. You cannot understand it by reading a timeline. Timelines explain. You cannot even fully understand it by listening to the song itself, beautiful as it is — because the song is already a finished object. It has been resolved. The dying man has already been named, the farewell has already been given its melody.

What we needed was something unresolved. Something that puts you *inside* the threshold, not outside looking at it.

Conversation was the only form we could think of that forces you to be present. When you speak to someone — even a constructed voice, even a character built from language models and emotional routing — you cannot be passive. The exchange demands something from you. You have to say something to receive something. And in that exchange, if the system is built right, what comes back is not an answer. It is a reflection.

The emotions of the people who lived through 1973 — the soldiers, the mothers, the poets, the protesters — are not accessible through explanation. They are accessible, however imperfectly, through conversation. Through the act of reaching toward them and having something reach back.

That is why we built a conversation and not an archive.

---

### II. What Caught Us: The Death Scene and What the War Left Behind

The song was written for a death. Not a metaphorical death, not a political death, but a literal one: a lawman bleeding out in the New Mexico dirt while his wife sits beside him and the world does not stop. Peckinpah filmed it in 1973, the same year the Paris Peace Accords were signed and America began the long, confused process of leaving Vietnam.

The parallel is not subtle, but it is honest. Thousands of men came home from Vietnam in that same condition — not necessarily physically dying, but carrying something that was ending inside them. The country they had left was gone. The certainty they had been promised was gone. And the culture waiting for them at home had already moved past the war, past the grief, into Watergate and gas shortages and the slow unraveling of the 1960s dream.

What caught us was not the war itself — we have no direct claim to that history — but its *effects*. The way violence does not stay in the place where it happened. The way a mother who watched her son board a bus in 1968 was still standing at the window in 1973, still watching, still waiting. The way the soldier who survived might have found that survival the hardest part of all.

The project tries to hold all of that without simplifying it. The five voices — Bob Dylan witnessing from the outside, the frontline soldier speaking from inside the violence, the waiting mother holding herself together at home, the future self looking back at what was lost, and the door itself standing at the end of every choice — are not meant to explain the era. They are meant to let you stand at different points within it and feel the weight differently from each position.

We kept coming back to the mother. The one who said goodbye before the war was over. The one who left the porch light on.

---

### III. AI as Mirror: What the System Reflected Back

We want to be honest about what AI did and did not do in this project.

It did not generate the creative vision. It did not decide that a dying sheriff's farewell was the right place to begin, or that a mother's vigil was the emotional center of the Vietnam era, or that the door was the right metaphor for the liminal space between who we were and who we became. Those decisions came from us, from reading, from listening to the song more times than we can count, from sitting with the question of what it actually means to knock on a door and not know whether you want it to open.

What AI did was *mirror*. And this is not a diminishment — it is the most precise word we have for what happened.

When the Groq model analyzed the emotional content of a user's message and returned a sentiment, an intensity, a theme — it was showing us what emotional meaning lived inside language. When the character router sent a particular voice to answer a particular turn of conversation, it was reflecting back a logic of human emotional resonance: grief belongs to the mother, rage belongs to the soldier, silence belongs to the door. When Gemini translated that emotion into a key, a tempo, a reverb level, a door state — it was building a mirror between interior state and exterior atmosphere.

The system reflects. It takes what you bring — your questions, your confessions, your silences — and it shows it back to you through the voices of people who lived inside a particular historical wound. You are not talking to a chatbot. You are talking to an echo chamber built from 1973, and the echo is shaped by what you carry.

This is what made the AI feel less like a tool and more like a mirror. A tool executes. A mirror shows you something you did not realize was already there. Several times during development, we would test the system by typing something we felt — something vague, personal, not historically specific — and the character that answered, and the way it answered, was more accurate than we expected. Not because the AI was guessing, but because the emotions we were feeding into it were the same emotions the system was built to recognize: longing, uncertainty, the particular weight of a question that has no good answer.

The mirror worked. That was both the technical success and the philosophical one.

---

### IV. Our Door: A Mother's Farewell and the Pain That Does Not Translate

The assignment asks: what does "Knockin' on Heaven's Door" mean in your own life? What transitions, farewells, or thresholds does this phrase evoke?

We keep returning to an image we cannot stop imagining, even though it is not ours. A mother standing at a door — not a symbolic door, a real one, with peeling paint and a screen that bangs in the wind — watching her son walk toward a bus or a truck or whatever conveyance was taking him away from her. She does not know if he will come back. She probably suspects he will not come back the same. She stands there until he is out of sight, and then she stands there a little longer, because the moment she turns away is the moment the leaving becomes real.

That moment is what the song is about, beneath everything else. It is about the threshold between before and after. Before the door opens, everything is still possible. After it opens, some things become impossible.

We think about farewell differently now than we did before building this project. Farewell is not an event. It is a posture — a sustained holding-on that happens even when you know you should let go. The mother in the song, the soldier in the field, the future self looking back: they are all in that posture. They are all still standing at the threshold, still holding something they cannot put down.

What this project means to us is that we spent months building a system that could hold that posture — that could sit at the threshold without resolving it, without telling you what is behind the door, without making the farewell any easier than it actually is. The system does not console. It witnesses. It says: *yes, this is how heavy this was. You are right to feel the weight of it.*

That is the only honest thing we could offer.

---

### V. Technical Reflection: What the Architecture Learned to Do

The system is built in three layers. The first layer is Groq's language model, which reads each message as an emotional document — not for its literal content but for what it reveals about the speaker's inner state. The second layer is the adaptive character router, which uses that emotional evidence to decide which voice is most honest for this moment. The third layer is Gemini, which translates the emotional state into atmospheric parameters: a key, a tempo, a reverb, a door position, a color palette.

The Tone.js audio engine on the frontend synthesizes music in real time from those parameters. The music does not play behind the conversation — it plays *with* it. When the conversation enters a register of grief, the music slows, the reverb opens, the key drops into minor. When the conversation finds something like hope, the tempo rises, the door in the visual canvas moves toward open, the light changes.

The most important technical choice was making these transitions perceptible but not theatrical. The system is not trying to manipulate you into an emotion. It is trying to be honest about the emotion that is already present. The difference matters.

We also want to acknowledge what the system cannot do. It cannot actually give voice to a Vietnamese soldier, or to a mother from Tennessee who lost her son in 1968, or to Bob Dylan. It can only work with approximations — carefully constructed, historically grounded, emotionally calibrated approximations. These voices are built from language models trained on the accumulated text of human experience. They are not the real people. They are echoes of the real people, shaped by what we know of how those people spoke, feared, grieved, and endured.

An echo is not the original sound. But it is proof that the original sound happened. It is proof that it traveled far enough to bounce back.

---

### Closing: Why We Knocked

We built this project because we believe the past is not over. The Vietnam War ended fifty years ago, but the emotional logic it contained — the logic of a mother watching a door, of a soldier who cannot find his way back from a violence he did not choose, of a generation whose idealism was spent and whose grief was dismissed — that logic is not historical. It is structural. It lives inside the shapes of farewell that every generation inherits.

Bob Dylan wrote a two-minute song about a dying man in a Western, and it became one of the most covered songs in the history of popular music. That does not happen because the lyrics are clever. It happens because the lyrics are true in the way that only the simplest things are true: *put my guns in the ground, I can't shoot them anymore.* The weight of what we carry. The relief of putting it down.

We hope this project offers one small way to stand at the door long enough to feel that weight — and to hear, from the other side, the voices of people who carried theirs all the way to the threshold.

---

*Built with Groq (llama-3.3-70b-versatile), Gemini 2.0 Flash, Tone.js, React, and FastAPI.*
*CSE 358 Introduction to Artificial Intelligence — Spring 2025–2026*
