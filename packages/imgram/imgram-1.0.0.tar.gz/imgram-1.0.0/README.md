# Imgram

Imgram is a Python CLI for downloading Instagram posts.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install Imgram.

```bash
pip install imgram
```

## Usage
Sometimes URLs contain an `&`. When that's the case, you must encase the URL with `"`. The same goes for paths with spaces in them.  
Anything prefixed by `?` can remain without issue

### Downloading a post to the current folder
```console
imgram URL
```
#### example:
```console
imgram https://www.instagram.com/p/DNksmWBvT0H
```

### Downloading a post to a specified folder
```console
imgram URL -o "path/to/folder"
imgram URL --output "path/to/folder"
```
#### examples:
```console
imgram https://www.instagram.com/p/DKeGhXcvPL6/?img_index=1 -o C:/Users/USER/Downloads/
imgram https://www.instagram.com/reel/DNYWdfmvHUq/?utm_source=ig_web_copy_link --output C:/Users/USER/Downloads/
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
