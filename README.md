# Video Recommendation System

This project implements a video recommendation system that suggests personalized videos based on user preferences and engagement patterns. The system utilizes a combination of content-based filtering, collaborative filtering, and cold-start mechanisms to generate recommendations. The application is built using Flask and leverages data from various APIs to fetch user interactions and video metadata.

## Objective

The objective of this project is to design a recommendation algorithm that can provide personalized video suggestions by leveraging user interaction data and video metadata obtained through APIs. The system handles the cold-start problem and provides recommendations based on user mood, interactions, and preferences.

## Technologies Used

- **Python**: For the backend logic.
- **Flask**: For creating the API endpoints.
- **Pandas**: For data processing and manipulation.
- **Scikit-learn**: For implementing machine learning algorithms (e.g., SVD, cosine similarity).
- **Numpy**: For mathematical operations and data manipulation.

## Features

### Content-based Filtering
Recommends videos based on the user's past interactions (viewed, liked, rated, inspired).

### Collaborative Filtering
Recommends videos based on similarities between users.

### Cold Start Solution
Recommends videos based on user mood when there's no prior interaction history.

### Hybrid Model
Combines content-based, collaborative filtering, and cold-start methods for improved recommendation accuracy.

## API Endpoints

- `GET /feed?username=<username>&category_id=<category_id>&mood=<user_mood>`:  
  Recommends videos based on user preferences, category, and mood.

- `GET /feed?username=<username>&category_id=<category_id>`:  
  Recommends videos based on user preferences and category.

- `GET /feed?username=<username>`:  
  Recommends videos based on user preferences only.

## Usage Guidelines

To get started with the project, follow the steps below:

1. **Clone the repository:**

   Use the following command to clone the repository to your local machine:

   ```bash
   git clone https://github.com/ashutoshkorde777/Video_Recommendation_Algorithm.git
Install dependencies:

Navigate to the project directory and install the required dependencies from the requirements.txt file:

```bash
cd Video_Recommendation_Algorithm
pip install -r requirements.txt
```
 **Run the application:**

Once the dependencies are installed, run the application using the command:

```bash
python app.py
```
The application will start, and you can begin using the video recommendation system.
