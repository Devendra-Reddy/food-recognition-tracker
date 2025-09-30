import kagglehub
import os

def download_dataset():
    """
    Download the Fruit Recognition and Calories Estimation dataset from Kaggle.
    This provides labeled fruit images for testing the computer vision model.
    Returns the path to the downloaded dataset files.
    """
    try:
        # Use kagglehub to download the specified dataset
        path = kagglehub.dataset_download("warcoder/fruit-recognition-and-calories-estimation")
        print(f"Dataset downloaded successfully!")
        print(f"Path to dataset files: {path}")
        
        # Verify download by listing contents
        if os.path.exists(path):
            files = os.listdir(path)
            print(f"Dataset contains {len(files)} items")
            
            # Display first few files as examples for verification
            sample_files = files[:5] if len(files) > 5 else files
            print("Sample files found:")
            for file in sample_files:
                print(f"  - {file}")
                
        return path
        
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        return None

if __name__ == "__main__":
    # Execute dataset download when script is run directly
    dataset_path = download_dataset()
    
    # Provide feedback on download status
    if dataset_path:
        print("\nDataset ready for use in testing!")
        print("You can now use these fruit images to test your Flask application.")
    else:
        print("Dataset download failed. Check your internet connection and Kaggle credentials.")
