import bot
import session_builder
import config

if __name__ == "__main__":
    # execute only if run as a script

    classDetails = {
        "clubName": "CF Kraków",
        "startTime": "08:00",
        "date": "2019-01-23",
        "trainer": "Michał Kubicz",
        "title": 'WOD Beginners'
    }

    perfectGymBot = bot.PerfectGymBot(session=session_builder.Session.build(), config=config.CFKrakowConfig)
