# Beginner's Guide to Your Framework

Think of your Python application like building a customized PC. You have a motherboard (`Context`), and you can plug in different parts like a graphics card or a hard drive (`Components`). You use a manual (`config.json`) to tell the motherboard exactly what parts you bought, what their settings are, and which parts need to connect to each other.

Here is the breakdown of how your code does this!

---

## 1. The Blueprint (`config.json`)
This is the master instruction manual. It has three main sections:
1. **Components**: "Hey, I want to use a Postgres database and an AgentSales."
2. **Configuration**: "Here are the usernames, passwords, and API keys for those components."
3. **Dependencies**: "Hey AgentSales, you are going to need to talk to Postgres, so I'm plugging Postgres into you."

## 2. The Motherboard (`context.py`)
When you run `python main.py config.json`, the `Context` is born. It reads your JSON blueprint and does the heavy lifting in three steps:

- **Step 1: Instantiation (`loadConfiguration`)** 
  It looks at your `"Components"` list and literally builds them. If it sees "Postgres", it creates a `PostgresDB` Python object. It stores all these empty objects in a list called `self.listComponents`.
- **Step 2: Configuration (`apply_configurations`)** 
  It looks at the `"Configuration"` section. It finds the `PostgresDB` object it just built and hands it the username and password. Now the object knows *how* to connect.
- **Step 3: Dependency Injection (`apply_dependencies`)** 
  It looks at the `"Dependencies"` section. It sees that `AgentSales` needs a database. It grabs the fully configured `PostgresDB` object and literally hands it over to `AgentSales`. 

## 3. The Parts (`component/`)
To make sure every part fits into the motherboard, they all have to follow the same rules. 
- **`component.py`**: This is the "shape" of the plug. It says, "If you want to be a Component in this app, you MUST have a `configure` method, a `connect` method, and a way to hold dependencies."
- **`dependency.py`**: A helper that ensures you don't accidentally plug the wrong thing in. If `AgentSales` asks for a Database, this makes sure it doesn't accidentally get handed a Redis cache.
- **`component_registry.py` & `component_factory.py`**: This is how the app translates the string `"Postgres"` in your JSON into an actual Python class. Every time a new component is created, it gets a `@registry("Name")` tag so the factory can find it.

## 4. The Action (`agent/sales.py` & `database/`)
These are the actual parts you built! 

**How `AgentSales` works:**
1. It inherits from `Component` (so it fits the motherboard).
2. It has a `dependencies` list at the top that says, "I strictly require a `PostgresDB` object, and I will call it 'db'."
3. When the app starts up (`connect`), `AgentSales` asks for its `'db'`. Because `context.py` already gave it the Postgres database in Step 3, `AgentSales` can now use `db.execute_request()` to talk to the database without ever needing to know the password or IP address!

## Summary of the Magic
The beauty of this architecture is that **AgentSales doesn't care where the database is**. You can completely change the Postgres password, move it to a different server, or even swap it for a different database, and you only have to change `config.json`. You never have to edit `sales.py`!
