
PATHS = {
    "green": {
        "name": "Right View",
        "audio": "view.mp3",
        "description": (
            "Right View is the wisdom to see things as they truly are. "
            "It means understanding that our actions have consequences and "
            "recognising how ignorance can lead to suffering. When we observe "
            "life clearly, without being controlled by assumptions or confusion, "
            "we develop greater wisdom and compassion."
        )
    },

    "blue": {
        "name": "Right Intention",
        "audio": "intention.mp3",
        "description": (
            "Right Intention means guiding our thoughts towards kindness, "
            "compassion and goodwill. It encourages us to let go of hatred, "
            "selfishness and harmful desires. Our intentions shape our actions, "
            "and when our thoughts come from a place of understanding and care, "
            "we create a more peaceful life for ourselves and others."
        )
    },

    "yellow": {
        "name": "Right Speech",
        "audio": "speech.mp3",
        "description": (
            "Our words have the power to heal or hurt. Right Speech teaches us "
            "to speak truthfully and kindly, avoiding lies, harsh words, gossip "
            "and speech that creates division. Before speaking, pause and ask "
            "yourself whether your words are true, helpful and peaceful. "
            "Thoughtful communication builds trust and understanding."
        )
    },

    "red": {
        "name": "Right Action",
        "audio": "action.mp3",
        "description": (
            "Right Action means living with kindness, honesty and respect for "
            "all living beings. It encourages us to avoid causing harm, taking "
            "what is not given and acting irresponsibly. Even small acts of "
            "kindness and consideration can make a meaningful difference. "
            "Let your actions reflect the values you believe in."
        )
    },

    "violet": {
        "name": "Right Livelihood",
        "audio": "livelihood.mp3",
        "description": (
            "Right Livelihood reminds us that the way we earn a living matters. "
            "It encourages honest and ethical work that does not exploit others "
            "or cause unnecessary suffering. Whatever our profession, we can "
            "choose to act with fairness, responsibility and respect. "
            "A meaningful life includes the way we contribute to the world."
        )
    },

    "purple": {
        "name": "Right Concentration",
        "audio": "concentration.mp3",
        "description": (
            "Right Concentration is the practice of training the mind to become "
            "calm, focused and steady. Through meditation and consistent practice, "
            "we learn to reduce distractions and develop deeper awareness. "
            "A concentrated mind sees more clearly and becomes less controlled "
            "by restless thoughts, allowing wisdom and inner peace to grow."
        )
    },

    "orange": {
        "name": "Right Mindfulness",
        "audio": "mindfulness.mp3",
        "description": (
            "Right Mindfulness means being aware of our thoughts, feelings, "
            "actions and surroundings. Instead of constantly dwelling on the "
            "past or worrying about the future, we learn to observe the present "
            "moment. With awareness, we can understand our reactions and respond "
            "with wisdom rather than acting on impulse."
        )
    },

    "brown": {
        "name": "Right Effort",
        "audio": "effort.mp3",
        "description": (
            "Right Effort is the steady commitment to personal growth. It means "
            "preventing harmful thoughts from arising, overcoming those that "
            "have already appeared, developing positive qualities and strengthening "
            "the good within us. Progress requires patience, discipline and "
            "continuous effort. Every sincere step forward matters."
        )
    }
}


def get_path(colour):
    if not isinstance(colour, str):
        return None

    return PATHS.get(colour.lower().strip())


if __name__ == "__main__":
    for colour, path in PATHS.items():
        print(f"{colour.upper()} → {path['name']} → {path['audio']}")
