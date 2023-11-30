
echo "Build Started"

pip3.9 install --disable-pip-version-check --target . --upgrade -r /vercel/path0/requirements.txt --use-deprecated=legacy-resolver
python3.9 manage.py collectstatic --noinput --clear
rm requirements.txt

echo "Build Completed"