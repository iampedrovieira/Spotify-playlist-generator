# Spotify Playlist Maker

This is a python script to create playlist automatically from tomorrowland line-up.

## Requirements
Docker (optional)
Python
Spotify app on developer.spotify.com

## Installation
Install package
```bash
pip install requirements.txt
```

## Usage
Run docker container
```bash
docker run -it -p 8080:5000 -v .:/home/app python-dev bash
```
Run flask app to get auth 
```bash
python getAuthorizationToken.py
```
Open your browser on  0.0.0.0:8080/login
Sign-in with your spotify account
Run script
```bashP
python createPlaylist.py
```
## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)