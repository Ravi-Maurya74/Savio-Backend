
echo "Build Started"

python3.9 -m pip install --upgrade pip
python3.9 -m pip install -r requirements.txt --use-deprecated=legacy-resolver
python3.9 manage.py collectstatic --noinput --clear
sudo rm requirements.txt

echo "Build Completed"