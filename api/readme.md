# marshalling - https://ifitzsimmons.medium.com/automated-dynamodb-data-marshaling-cadb4665a6a0

https://stackoverflow.com/questions/27894393/is-it-possible-to-save-datetime-to-dynamodb

According to alejandro-franco response .isoformat() make the trick.

Just tested and this a working example:

CustomerPreferenceTable.put_item(
    Item={
        "id": str(uuid4()),
        "validAfter": datetime.utcnow().isoformat(),
        "validBefore": (datetime.utcnow() + timedelta(days=365)).isoformat(),
        "tags": ["potato", "eggplant"]
    }
)
Share
Improve this answer
Follow
answered Jan 4, 2018 at 19:16
user1855042's user avatar
user1855042
60166 silver badges55 bronze badges
2
Just be aware that datetime.utcnow() does not return a date with timezone information. So while parsing back, you should be knowing that stored information is UTC. Rather than that I would use datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(), this way the generated information would be easily parsed with datetime.fromisoformat(). – 
ᐅdevrimbaris
 