from backend.database import SessionLocal, engine
from backend.models import Base, User, Note
from backend.ranking_dataset import RANKING_DATASET

SEED_USERS = [
    {
        "id": 1,
        "name": "Alice",
        "email": "alice@example.com",
        "password": "alicepass123"
    },
    {
        "id": 2,
        "name": "Bob",
        "email": "bob@example.com",
        "password": "bobpass123"
    }
]

SEED_NOTES = [
    {
        "id": 1,
        "owner_id": 1,
        "title": "Standup Summary",
        "tag": "work",
        "content": "Discussed sprint progress, blockers on the payments API integration, and the plan for the demo on Friday."
    },
    {
        "id": 2,
        "owner_id": 1,
        "title": "Sprint Retro Notes",
        "tag": "work",
        "content": "Retro highlighted communication gaps between frontend and backend teams and agreed on daily syncs going forward."
    },
    {
        "id": 3,
        "owner_id": 2,
        "title": "One on One",
        "tag": "work",
        "content": "Quick check-in, no blockers, discussed career growth goals for next quarter."
    },
    {
        "id": 4,
        "owner_id": 1,
        "title": "Morning Run",
        "tag": "health",
        "content": "Ran 5km along the river trail before breakfast, felt great."
    },
    {
        "id": 5,
        "owner_id": 2,
        "title": "Doctor Visit",
        "tag": "health",
        "content": "Annual checkup went well, blood pressure normal, scheduled next visit in six months."
    },
    {
        "id": 6,
        "owner_id": 1,
        "title": "Pasta Recipe",
        "tag": "recipes",
        "content": "Boil pasta, saute garlic in olive oil, add tomatoes, basil, and a pinch of chili flakes."
    },
    {
        "id": 7,
        "owner_id": 2,
        "title": "Smoothie Recipe",
        "tag": "recipes",
        "content": "Blend banana, spinach, almond milk, and a spoon of peanut butter for breakfast."
    },
    {
        "id": 8,
        "owner_id": 1,
        "title": "Flight Booking",
        "tag": "travel",
        "content": "Booked a round trip flight for the December vacation, window seat confirmed."
    },
    {
        "id": 9,
        "owner_id": 2,
        "title": "Random Thought",
        "tag": "random",
        "content": "Maybe the library needs a better recommendation system based on reading history."
    },
    {
        "id": 10,
        "owner_id": 1,
        "title": "Quote To Remember",
        "tag": "random",
        "content": "Done is better than perfect, keep shipping."
    },
    {
        "id": 23,
        "owner_id": 2,
        "title": "Payment Gateway Timeout",
        "tag": "ai-demo",
        "content": "Payment gateway requests are timing out during peak traffic and causing checkout failures."
    },
    {
        "id": 24,
        "owner_id": 2,
        "title": "Database Connection Pool",
        "tag": "ai-demo",
        "content": "Database connection pool is exhausted when traffic spikes, causing slow API responses."
    },
    {
        "id": 25,
        "owner_id": 2,
        "title": "API Latency Investigation",
        "tag": "ai-demo",
        "content": "API latency increased after the latest deployment and engineers are investigating slow downstream services."
    },
    {
        "id": 26,
        "owner_id": 2,
        "title": "Cache Invalidation Issue",
        "tag": "ai-demo",
        "content": "Stale cache entries are returning outdated restaurant information after menu updates."
    },
    {
        "id": 27,
        "owner_id": 2,
        "title": "Order Service Recovery",
        "tag": "ai-demo",
        "content": "Order processing recovered after restarting the affected service and clearing failed requests."
    },
    {
        "id": 28,
        "owner_id": 2,
        "title": "Monitoring Alert Spike",
        "tag": "ai-demo",
        "content": "Monitoring alerts increased sharply because several backend services reported elevated error rates."
    },
    {
        "id": 29,
        "owner_id": 2,
        "title": "Deployment Rollback",
        "tag": "ai-demo",
        "content": "The latest deployment was rolled back after it introduced errors in the checkout workflow."
    },
    {
        "id": 30,
        "owner_id": 2,
        "title": "Incident Communication",
        "tag": "ai-demo",
        "content": "The support team coordinated incident updates and shared recovery progress with stakeholders."
    }
]

AI_SAMPLE_NOTES = [
    {
        "owner_id": 2,
        "title": "Morning workout plan",
        "content": "Do 30 minutes of cardio followed by strength training focused on legs and core.",
        "tag": "ai-demo"
    },
    {
        "owner_id": 2,
        "title": "Grocery list",
        "content": "Buy milk, eggs, spinach, chicken breast, and whole wheat bread for the week.",
        "tag": "ai-demo"
    },
    {
        "owner_id": 2,
        "title": "Project deadline reminder",
        "content": "The backend API for the Zomato Notes capstone must be deployed and demoed by Friday.",
        "tag": "ai-demo"
    },
    {
        "owner_id": 2,
        "title": "Book recommendation",
        "content": "A friend suggested reading a novel about a detective solving crimes in a coastal town.",
        "tag": "ai-demo"
    },
    {
        "owner_id": 2,
        "title": "Recipe idea",
        "content": "Try making a vegetable stir fry with broccoli, bell peppers, and soy sauce tonight.",
        "tag": "ai-demo"
    },
    {
        "owner_id": 2,
        "title": "Gym schedule change",
        "content": "Switch leg day to Thursday and move the rest day to Sunday this week.",
        "tag": "ai-demo"
    },
    {
        "owner_id": 2,
        "title": "Meeting notes",
        "content": "Discussed the database schema for the notes app and agreed on using foreign keys for ownership.",
        "tag": "ai-demo"
    },
    {
        "owner_id": 2,
        "title": "Weekend hiking trip",
        "content": "Plan a short hiking trip to a nearby trail, pack water bottles and snacks in advance.",
        "tag": "ai-demo"
    }
]

Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    db.query(Note).delete()
    db.query(User).delete()

    for user_data in SEED_USERS:
        db.add(User(**user_data))

    for note_data in SEED_NOTES:
        db.add(Note(**note_data))

    for item in RANKING_DATASET:
        db.add(
            Note(
                owner_id=1,
                title=item["title"],
                content=item["content"],
                tag="kb-demo"
            )
        )

    for item in AI_SAMPLE_NOTES:
        db.add(Note(**item))

    db.commit()

    print("Database seeded successfully.")
    print("2 users added.")
    print("18 core and AI incident notes added.")
    print("12 ranking notes added.")
    print("8 semantic-search notes added.")
    print("38 notes added in total.")

finally:
    db.close()