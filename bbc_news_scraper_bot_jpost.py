import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


# scraping function
def scrape_news(news_site):
    logger.info(f'Scraping {news_site} News...')

    if news_site == 'bbc':
        url = 'https://www.bbc.com/news'
        headline_selectors = [
            {'tag': 'h2', 'class': 'sc-4fedabc7-3 dsoipF', 'data-testid': 'card-headline'},
            {'tag': 'h2', 'class': 'sc-4fedabc7-3 zTZri', 'data-testid': 'card-headline'},
        ]
        link_prefix = 'https://www.bbc.com'

    elif news_site == 'jpost':
        url = 'https://www.jpost.com/'
        headline_selectors = [
            {'tag': 'h3', 'class': 'top-story-large-item-title-new draft-title-cms'},
            {'tag': 'h3', 'class': 'category-five-articles-large-item-title draft-title-cms'},
        ]
        link_prefix = 'https://www.jpost.com/'

    else:
        return "The news website you selected is not supported by this bot."

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        all_titles_links = []

        for selector in headline_selectors:
            titles = soup.find_all(selector['tag'], class_=selector['class'])
            for title in titles:
                link_tag = title.find_parent('a')
                if link_tag and 'href' in link_tag.attrs:
                    link = link_tag['href']
                    if not link.startswith('http'):
                        link = link_prefix + link
                    all_titles_links.append((title.get_text(strip=True), link))

        all_titles_links = list(set(all_titles_links))

        if not all_titles_links:
            return "No titles found. Please check the HTML structure and tag/class names."
        else:
            headlines = ""
            for index, (title, link) in enumerate(all_titles_links, start=1):
                headlines += f"{index}. {title}\nLink: {link}\n\n"
            return headlines
    else:
        return f"Failed to retrieve the web page. Status code: {response.status_code}"


# Command handler for /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hi! Send "bbc" or "jpost" to get the latest news headlines.')


# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.lower()
    headlines = scrape_news(text)
    if len(headlines) > 4096:
        for i in range(0, len(headlines), 4096):
            await update.message.reply_text(headlines[i:i + 4096])
    else:
        await update.message.reply_text(headlines)


# Main function to run the bot
def main():
    application = Application.builder().token('replace with your bot token from botfather').build()
#in order to get your own bot token, go to telegram and search 'botfather'.
#then type '/newbot'' follow the instruction and you will get your own token.

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()


if __name__ == '__main__':
    main()
