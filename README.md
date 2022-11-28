Setup
--

install sox
install ffmpeg

python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

export AWS_DEFAULT_REGION=us-west-2
export AWS_ACCESS_KEY_ID=YOUR KEY
export AWS_SECRET_ACCESS_KEY=YOUR KEY
export GOOGLE_APPLICATION_CREDENTIALS=vendors/google.json
export ASSEMBLY_TOKEN=YOUR TOKEN

Add keys.json file to vendors folder

Example
--

python3 benchmark.py --with_azure True --with_speechmatics True --directory test

Distributing
--
zip -r benchmark-report-cli.zip . -x ".git/*" "env/*" "test/*" ".gitignore"
