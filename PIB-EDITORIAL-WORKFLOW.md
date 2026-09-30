# PIB Editorial Workflow

Lex Talk Legal uses the official PIB press-release RSS as a **discovery radar**, not as an automatic article-copying system.

## Flow

PIB RSS → legal/recovery/policy filter → `data/pib_queue.json` → editorial review → original Lex Talk Legal article → Blogger → existing editorial sync → website

## Queue fields

- `title`: official PIB title
- `url`: official PIB release URL
- `published`: PIB publication timestamp when available
- `category`: suggested Lex Talk Legal section
- `summary`: short feed description
- `status`: starts as `review`
- `editorial_action`: reminder that the item needs editorial treatment before publication

## Editorial rule

Do not copy the full PIB release into the site automatically. Before publication, verify the official release and add useful Lex Talk Legal context, such as who is affected, what changed, dates/effective dates, relevant law or regulation, and a clear link to the official source.
