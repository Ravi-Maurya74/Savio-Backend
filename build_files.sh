
echo "Build Started"

python3.9 -m pip3.9 install --upgrade pip
python3.9 -m pip3.9 install -r requirements.txt --use-deprecated=legacy-resolver
python3.9 manage.py collectstatic --noinput --clear
rm requirements.txt

echo "Build Completed"