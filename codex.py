from flask import Flask, request, render_template
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
import requests
import logging
from parsel import Selector
import os

logging.basicConfig(level=logging.INFO)

app = Flask(__name__, template_folder='.')

try:
    model = pickle.load(open('random_forest_model.pkl', 'rb'))
except Exception as e:
    logging.error(f"Error loading model: {e}")

@app.route('/')
def hello_world():
    return render_template("Project.html")

@app.route('/predict', methods=['POST'])
def predict():
    video_link = request.form['A_link']
    video_title_length, views, post_date, likes = get_video_data(video_link)

    try:
        post_date_dt = pd.to_datetime(post_date, errors='coerce')
        if pd.isna(post_date_dt):
            return render_template('Project.html',
                                   pred='Invalid date format. Please use dd-MM-Y.',
                                   bhai="Check the date format and try again.")

        current_date = datetime.now()
        video_age = (current_date - post_date_dt).days

        features = np.array([[video_title_length, int(views), int(likes), video_age]])
        prediction = model.predict_proba(features)
        output = prediction[0][1]
        foutput = output * 100

        threshold = 0.5
        viral_flag = 1 if output > threshold else 0

        csv_file = "Youtube_Data.csv"

        if os.path.exists(csv_file):
            try:
                df_existing = pd.read_csv(csv_file)
                if not df_existing.empty and "ID" in df_existing.columns:
                    new_id = df_existing["ID"].max() + 1
            except Exception as e:
                logging.warning(f"Could not read existing CSV file properly: {e}")

        data_row = pd.DataFrame([{
            'ID': new_id,
            'category': "Not Discovered",
            'video_title_length': video_title_length,
            'likes': int(likes),
            'views': views,
            'post_date': post_date,
            'channel_url': video_link,
            'channel_name': "Unknown Channel",
            'video_url': video_link,
            'Viral': viral_flag
        }])

        try:
            data_row.to_csv(csv_file, mode='a', index=False, header=not os.path.exists(csv_file))
            logging.info(f"Saved to {csv_file} with ID {new_id}")
        except Exception as e:
           logging.error(f"Error saving data row: {e}")

        if output > threshold:
            return render_template('Project.html',
                                   pred=f'Your Video is likely to go viral.\nProbability of going viral is {foutput:.2f}%',
                                   bhai="Consider sharing it more widely!")
        else:
            return render_template('Project.html',
                                   pred=f'Your Video is less likely to go viral.\nProbability of going viral is {foutput:.2f}%',
                                   bhai="Your Video might need more promotion.")

    except (ValueError, KeyError) as e:
        logging.error(f"Error during prediction: {e}")
        return render_template('Project.html',
                               pred='An error occurred. Please check your input data.',
                               bhai="Please ensure all inputs are correct and try again.")

def get_video_data(video_url):
    try:
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'cache-control': 'max-age=0',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            'sec-ch-ua-arch': '"x86"',
            'sec-ch-ua-bitness': '"64"',
            'sec-ch-ua-form-factors': '"Desktop"',
            'sec-ch-ua-full-version': '"127.0.6533.90"',
            'sec-ch-ua-full-version-list': '"Not)A;Brand";v="99.0.0.0", "Google Chrome";v="127.0.6533.90", "Chromium";v="127.0.6533.90"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"15.0.0"',
            'sec-ch-ua-wow64': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'service-worker-navigation-preload': 'true',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'x-client-data': 'CKe1yQEIkrbJAQijtskBCImSygEIqZ3KAQiI88oBCJahywEInf7MAQiFoM0BCNWszgEIva3OAQjWr84BCOWvzgEIvrbOAQjZt84BCIi4zgEYwcvMARignc4BGLquzgEYmrHOAQ==',
        }
        response = requests.get(video_url, headers=headers)
    except Exception as e:
        print('Response issue in scraping', e)

    respo = response.text
    dom = Selector(text=respo)
    video_title_length = len(dom.xpath('//meta[@name="title"]/@content').get(''))
    views = dom.xpath('//meta[@itemprop="interactionCount"]/@content').get('0')
    publish_date = dom.xpath('//meta[@itemprop="datePublished"]/@content').get('').split('T')[0]
    likes = respo.split('like this video along with ')[1].split('"')[0].replace(' other people', '').replace(',', '')
    return video_title_length, views, publish_date, likes

if __name__ == '__main__':
    app.run(debug=True)
