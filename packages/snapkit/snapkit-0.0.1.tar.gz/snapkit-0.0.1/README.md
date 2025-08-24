### Go inside of the parent folder 

### Install using pip

``` pip install . ```

### Check installation

```
    from snapkit  import jpg_to_png

    jpg_to_png(
        input_dir= "./your_input_dir",
        output_dir= "./your_output_dir",
        max_threads= 10 , # Optional deafult to cpu count
    )
```

### Setup 

`py -3.10 -m venv .venv`

`pip install -r .\requirements.txt`

`.\.venv\Scripts\activate`

Create setup wheel for `pip` installation

`python .\setup.py sdist bdist_wheel`

Install Current version

`pip install .\snapkit-0.0.1-py3-none-any.whl`

`pip install .` (without creating setup tools, setup.py is required)
