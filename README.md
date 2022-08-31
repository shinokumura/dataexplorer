# dataexplorer
## History
                  March 2021   first commit
                  June  2021   production version
                  Aug   2022   add new libraries (tendl.2021 and jendl5.0:)

## Readme
This is a Dash/Plotly based web application for the dissemination and visualize of [TALYS-Related Software and Databases](https://nds.iaea.org/talys/). The application is available at [dataexplorer](https://nds.iaea.org/dataexplorer/).

## Install
1. Download the repository by following command from the terminal:

    ```
    git clone https://github.com/shinokumura/dataexplorer.git
    ```

2. Create virtual environment either using virtualenv or conda.

3. Install the dependencies using following command:

    ```
    pip install -r requirements.txt
    ```

4. Download all datafiles of [EXFORtables](https://nds.iaea.org/talys/codes/exfortables.tar) and [ENDFtables](https://nds.iaea.org/talys/codes/endftables.tar) and untar them.

5. Change path to the datafiles and ```DEVENV = True``` in ```config.py```.

6. Run 

    ```
    python app.py
    ```