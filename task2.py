import string
import argparse
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import requests
import matplotlib.pyplot as plt
import logging

# Налаштування логування
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def get_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Перевірка на помилки HTTP
        logging.info(f"Успішно завантажено текст з {url}")
        return response.text
    except requests.RequestException as e:
        logging.error(f"Не вдалося завантажити текст з {url}: {e}")
        return None


def remove_punctuation(text):
    return text.translate(str.maketrans("", "", string.punctuation))


def map_function(word):
    return word, 1


def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()


def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)


def map_reduce(text):
    text = remove_punctuation(text)
    words = text.split()

    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))

    shuffled_values = shuffle_function(mapped_values)

    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    logging.info("MapReduce обробка завершена")
    return dict(reduced_values)


def visualize_top_words(word_counts, top_n=10):
    top_words = sorted(word_counts.items(),
                       key=lambda item: item[1], reverse=True)[:top_n]
    words, counts = zip(*top_words)

    plt.figure(figsize=(10, 8))
    plt.bar(words, counts, color='blue')
    plt.xlabel('Words')
    plt.ylabel('Frequency')
    plt.title('Top Words by Frequency')
    plt.xticks(rotation=45)
    plt.show()
    logging.info("Візуалізація топ-слів завершена")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Аналіз частоти слів з тексту по URL і візуалізація результатів")
    parser.add_argument('--url', type=str, required=True,
                        help='URL для завантаження тексту')
    args = parser.parse_args()

    text = get_text(args.url)
    if text:
        result = map_reduce(text)
        visualize_top_words(result, 10)
    else:
        logging.error("Текст не завантажено, візуалізація не можлива")