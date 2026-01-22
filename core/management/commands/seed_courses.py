from django.core.management.base import BaseCommand
from core.models import Course, Topic, TopicContent
from django.utils.text import slugify

class Command(BaseCommand):
    help = "Seeds initial cybersecurity courses, topics, and content."

    def handle(self, *args, **kwargs):
        Course.objects.all().delete()
        Topic.objects.all().delete()
        TopicContent.objects.all().delete()

        self.stdout.write(self.style.WARNING("🧹 Cleared old course data..."))

        courses_data = [
            {
                "title": "Cybersecurity Basics",
                "desc": "Learn how to protect yourself online from hackers, scams, and privacy threats.",
                "topics": [
                    ("Introduction to Cybersecurity", [
                        ("What is Cybersecurity?", "Cybersecurity is the practice of protecting systems, networks, and programs from digital attacks."),
                        ("Why Cybersecurity Matters", "Because digital threats are everywhere, and awareness is the first step to defense.")
                    ]),
                    ("Common Threats", [
                        ("Phishing", "Phishing is when attackers trick users into giving up sensitive information."),
                        ("Malware", "Malware refers to software designed to harm or exploit devices.")
                    ]),
                    ("Safe Browsing", [
                        ("Password Hygiene", "Use strong, unique passwords and two-factor authentication."),
                        ("Avoiding Scams", "Always verify links and sender identities.")
                    ])
                ]
            },
            {
                "title": "Ethical Hacking Essentials",
                "desc": "Understand how hackers think to protect systems better.",
                "topics": [
                    ("What is Ethical Hacking?", [
                        ("Purpose of Ethical Hacking", "It’s used to strengthen systems by finding vulnerabilities before criminals do."),
                        ("Types of Hackers", "White Hat, Black Hat, and Gray Hat hackers differ in intent.")
                    ]),
                    ("Reconnaissance", [
                        ("Footprinting", "Gathering information about a target system."),
                        ("Scanning", "Identifying open ports and services.")
                    ]),
                    ("Exploitation Basics", [
                        ("Exploits & Payloads", "Learn how exploits are used to gain unauthorized access."),
                        ("Post-Exploitation", "Understanding persistence and data exfiltration.")
                    ])
                ]
            },
            {
                "title": "Web Security & OWASP",
                "desc": "Master the top 10 web vulnerabilities and how to prevent them.",
                "topics": [
                    ("OWASP Top 10 Overview", [
                        ("What is OWASP?", "An open community focused on improving software security."),
                        ("Top 10 List", "Includes SQL Injection, XSS, CSRF, and more.")
                    ]),
                    ("SQL Injection", [
                        ("Concept", "Attackers manipulate queries through input fields."),
                        ("Prevention", "Always use parameterized queries.")
                    ]),
                    ("Cross-Site Scripting (XSS)", [
                        ("Concept", "Injecting malicious scripts into web pages."),
                        ("Prevention", "Escape user inputs and use Content Security Policy.")
                    ])
                ]
            },
            {
                "title": "Digital Forensics",
                "desc": "Learn to trace digital footprints and analyze cyber incidents.",
                "topics": [
                    ("Introduction to Forensics", [
                        ("Definition", "Digital forensics is the process of uncovering and interpreting electronic data."),
                        ("Chain of Custody", "Maintaining data integrity throughout investigations.")
                    ]),
                    ("Forensic Tools", [
                        ("Autopsy", "A popular open-source digital forensics platform."),
                        ("Wireshark", "Network packet analyzer used for monitoring traffic.")
                    ])
                ]
            },
            {
                "title": "Cyber Awareness for All",
                "desc": "Everyday safety tips to keep your digital life secure.",
                "topics": [
                    ("Phishing Awareness", [
                        ("Spotting Fake Emails", "Check sender address, grammar, and links."),
                        ("Social Engineering", "Attackers manipulate people into revealing info.")
                    ]),
                    ("Password Safety", [
                        ("Strong Passwords", "Use a mix of uppercase, lowercase, symbols, and numbers."),
                        ("Password Managers", "Tools like Bitwarden and 1Password help store passwords securely.")
                    ])
                ]
            }
        ]

        for course_data in courses_data:
            course = Course.objects.create(
                title=course_data["title"],
                slug=slugify(course_data["title"]),
                short_description=course_data["desc"],
                detail=course_data["desc"]
            )

            for i, (topic_title, lessons) in enumerate(course_data["topics"], start=1):
                topic = Topic.objects.create(
                    course=course,
                    title=topic_title,
                    slug=slugify(f"{course.slug}-{topic_title}"),
                    order=i
                )

                for j, (lesson_title, body) in enumerate(lessons, start=1):
                    TopicContent.objects.create(
                        topic=topic,
                        title=lesson_title,
                        body=body,
                        order=j
                    )

        self.stdout.write(self.style.SUCCESS("✅ Successfully seeded real cybersecurity courses!"))
