# Footwear Suggestion based on Foot Photo Analysis Project

This project measures foot size using image processing techniques. It involves capturing an image of a foot on a reference paper, processing the image to determine foot dimensions, and providing footwear recommendations based on these measurements.

## Features
- Capture an image of a foot on a reference paper.
- Process the image to extract foot measurements.
- Provide footwear recommendations based on foot size.
- Web-based interface for user interaction.


## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/prajnashankarimn/Feet-and-Footwear.git.git
    cd foot-size-measurement
    ```

2. Create a virtual environment:

    ```bash
    python -m venv venv
    ```

3. Activate the virtual environment:

    On Windows:

    ```bash
    venv\Scripts\activate
    ```

    On macOS/Linux:

    ```bash
    source venv/bin/activate
    ```

4. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. **Prepare your image:**

    Ensure the image is taken with the foot centered and touching one edge of the reference paper. The background should be white, and the floor color should differ from white.

2. **Create Databases:**

    Create the following databases: `zappos`, `amazon`, `flipkart`. In each database, create two collections: `female` and `male`.

3. **Import CSV Files:**

    Place your CSV files in the `database-cm/url` folder.

4. **Start the Flask application:**

    ```bash
    python app.py
    ```
    
5. **Open your web browser and go to:**

    [http://localhost:5000](http://localhost:5000)

    This will open the web interface where you can upload images and view results.

6. **Upload the image:**

    Navigate to the web interface (usually [http://localhost:5000](http://localhost:5000) when running locally). Use the upload button to select and upload the image file.

7. **View results:**

    After processing, the application will display the calculated foot size. Footwear recommendations based on the measurement will be shown on the results page.
