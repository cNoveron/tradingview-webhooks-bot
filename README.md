![demopic](https://user-images.githubusercontent.com/38849824/160300853-ef6fe753-36d6-41a9-9bd2-8a06f7add71d.png)

![](https://img.shields.io/github/license/robswc/tradingview-webhooks-bot?style=for-the-badge)
![](https://img.shields.io/github/commit-activity/y/robswc/tradingview-webhooks-bot?style=for-the-badge)
![](https://img.shields.io/twitter/follow/robswc?style=for-the-badge)

[tvwb_demo.webm](https://user-images.githubusercontent.com/38849824/192352217-0bd08426-98b7-4188-8e5b-67d7aa93ba09.webm)

### 📀 Live Demo 🖥
**There's now a live demo available at [http://tvwb.robswc.me](http://tvwb.robswc.me).
Feel free to check it out or send it some webhooks!**

[![DigitalOcean Referral Badge](https://web-platforms.sfo2.cdn.digitaloceanspaces.com/WWW/Badge%201.svg)](https://www.digitalocean.com/?refcode=2865cad8f863&utm_campaign=Referral_Invite&utm_medium=Referral_Program&utm_source=badge)

### [Get Support on Discord](https://discord.gg/wrjuSaZCFh)


# The What 🔬

Tradingview-webhooks-bot (TVWB) is a small, Python-based framework that allows you to extend or implement your own logic
using data from [Tradingview's webhooks](https://www.tradingview.com/support/solutions/43000529348-about-webhooks/). TVWB is not a trading library, it's a framework for building your own trading logic.

# The How 🏗

TVWB is fundamentally a set of components with a webapp serving as the GUI. TVWB was built with event-driven architecture in mind that provides you with the building blocks to extend or implement your own custom logic.
TVWB uses [Flask](https://flask.palletsprojects.com/en/2.2.x/) to handle the webhooks and provides you with a simple API to interact with the data.

# Quickstart 📘

## 🚀 **Quick Start Commands**

### **1. Build and Run with Nginx (Recommended - Most Secure)**
```bash
# Build the Docker image
docker-compose -f docker-compose.nginx.yml build

# Start the services (app + nginx)
docker-compose -f docker-compose.nginx.yml up -d

# Check status
docker-compose -f docker-compose.nginx.yml ps

# View logs
docker-compose -f docker-compose.nginx.yml logs -f app
```

### **2. Access Your Application**
```bash
# Get your GUI key
docker-compose -f docker-compose.nginx.yml exec app cat .gui_key

# Access the dashboard (replace YOUR_GUI_KEY with the actual key)
curl "http://localhost?guiKey=YOUR_GUI_KEY"
# or open in browser: http://localhost?guiKey=YOUR_GUI_KEY
```

### **3. Alternative: Run Without Nginx (Development)**

#### **Option A: Using Docker Compose (Original)**
```bash
# Build and run just the app
docker-compose up -d

# Access directly on port 5000
curl "http://localhost:5000?guiKey=YOUR_GUI_KEY"
```

#### **Option B: Run Locally (No Docker)**
```bash
# Install dependencies
cd src
pip install -r requirements.txt

# Run the app
python tvwb.py start --open-gui  # Open mode (no auth required)
# OR
python tvwb.py start  # Closed mode (requires GUI key)
```

## 📋 **Useful Commands**

### **Stop Services**
```bash
# Stop nginx setup
docker-compose -f docker-compose.nginx.yml down

# Stop original setup
docker-compose down
```

### **View Logs**
```bash
# All services
docker-compose -f docker-compose.nginx.yml logs -f

# Just the app
docker-compose -f docker-compose.nginx.yml logs -f app

# Just nginx
docker-compose -f docker-compose.nginx.yml logs -f nginx
```

### **Rebuild After Code Changes**
```bash
# Rebuild and restart
docker-compose -f docker-compose.nginx.yml build --no-cache
docker-compose -f docker-compose.nginx.yml up -d
```

## 🎯 **Recommended Workflow**

1. **Start with nginx setup** (most secure):
   ```bash
   docker-compose -f docker-compose.nginx.yml up -d
   ```

2. **Get your GUI key**:
   ```bash
   docker-compose -f docker-compose.nginx.yml exec app cat .gui_key
   ```

3. **Access at** `http://localhost?guiKey=YOUR_KEY`

4. **Monitor logs**:
   ```bash
   docker-compose -f docker-compose.nginx.yml logs -f app
```

## 🔍 **Troubleshooting**

- **Port 80 in use?** Check with `sudo lsof -i :80`
- **Container not starting?** Check logs with `docker-compose -f docker-compose.nginx.yml logs`
- **Code changes not working?** Rebuild with `--no-cache` flag

## 📚 **Installation Options**

* [Docker](https://github.com/robswc/tradingview-webhooks-bot/wiki/Docker) (recommended)
* [Manual](https://github.com/robswc/tradingview-webhooks-bot/wiki/Installation)

## 🌐 **Hosting**

* [Deploying](https://github.com/robswc/tradingview-webhooks-bot/wiki/Hosting)
  * [Cloud](https://github.com/robswc/tradingview-webhooks-bot/wiki/Hosting#cloud-hosting) (recommended)
  * [Local](https://github.com/robswc/tradingview-webhooks-bot/wiki/Hosting#using-a-personal-pc)


---
Ensure you're in the `src` directory. When running the following commands, **if you installed manually**.
**If you used docker**,
start the tvwb.py shell with `docker-compose run app shell` (in the project root directory) and omit the `python3 tvwb.py` portion of the commands.

---
### Creating an action

```bash
python3 tvwb.py action:create NewAction --register
```

This creates an action and automatically registers it with the app.  [Learn more on registering here](https://github.com/robswc/tradingview-webhooks-bot/wiki/Registering).

_Note, action and event names should **_always_** be in PascalCase._

You can also check out some "pre-made" [community actions](https://github.com/robswc/tradingview-webhooks-bot/tree/master/src/components/actions/community_created_actions)!

### Linking an action to an event

```bash
python3 tvwb.py action:link NewAction WebhookReceived
```

This links an action to the `WebhookReceived` event.  The `WebhookReceived` event is fired when a webhook is received by the app and is currently the only default event.

### Editing an action

Navigate to `src/components/actions/NewAction.py` and edit the `run` method.  You will see something similar to the following code.
Feel free to delete the "Custom run method" comment and replace it with your own logic.  Below is an example of how you can access
the webhook data.

```python
class NewAction(Action):
    def __init__(self):
        super().__init__()

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)  # this is required
        """
        Custom run method. Add your custom logic here.
        """
        data = self.validate_data()  # always get data from webhook by calling this method!
        print('Data from webhook:', data)
```

### Running the app

```bash
python3 tvwb.py start
```

### Sending a webhook

Navigate to `http://localhost:5000`.  Ensure you see the `WebhookReceived` Event.  Click "details" to expand the event box.
Find the "Key" field and note the value.  This is the key you will use to send a webhook to the app.  Copy the JSON data below,
replacing "YOUR_KEY_HERE" with the key you copied.

```json
{
    "key": "YOUR_KEY_HERE",
    "message": "I'm a webhook!"
}
```

The `key` field is required, as it both authenticates the webhook and tells the app which event to fire.  Besides that, you can
send any data you want.  The data will be available to your action via the `validate_data()` method. (see above, editing action)

On tradingview, create a new webhook with the above JSON data and send it to `http://ipaddr:5000/webhook`.  You should see the data from the webhook printed to the console.

### FAQs

#### So how do I actually trade?

To actually submit trades, you will have to use a library like [ccxt](https://github.com/ccxt/ccxt) for crypto currency.  For other brokers, usually there are
SDKs or APIs available.  The general workflow would look something like: webhook signal -> tvwb (use ccxt here) -> broker.  Your trade submission would take place within the `run` method of a custom action.

#### The tvwb.py shell

You can use the `tvwb.py shell` command to open a python shell with the app context.  This allows you to interact with the app without having to enter `python3 tvwb.py` every time.

#### Running Docker on Windows/Mac?

Thanks to @khamarr3524 for pointing out there are some docker differences when running on Windows or Mac.  I've added OS-specific `docker-compose.yml` files to accomodate these differences.  One should be able to run their respective OS's `docker-compose.yml` file without issue now!

#### How do I get more help?

At the moment, the wiki is under construction.  However, you may still find some good info on there.  For additional assistance you can DM me on [Twitter](https://twitter.com/robswc) or join the [Discord](https://discord.gg/wrjuSaZCFh).  I will try my best to get back to you!
