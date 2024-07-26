#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' 


echo "⠀⠀⠀⠀⠀⣠⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀"
echo "⠀⠀⠀⠀⠀⣿⠙⢦⡀⠀⠀⣰⢶⠀⠀⠀"
echo "⠀⠀⠀⠀⠀⢻⠀⠀⠹⣦⠞⠁⢸⠀⠀⠀"
echo "⠀⠸⡟⠓⠒⠛⠀⡀⠤⠤⢀⠀⠾⠶⢶⡆"
echo "⠀⠀⢻⡀⠀⡐⠁⠀⠀⠀⠀⠑⡀⢀⡞⠀"
echo "⣀⡤⠞⠃⢰⠀⠐⠒⠲⡶⠶⠶⢶⠘⠲⣄"
echo "⠙⠲⣤⡀⢸⠀⡒⠖⠒⡲⡒⠒⢒⢢⡞⠉"
echo "⢀⡴⠋⠀⡸⠀⠌⠀⠈⢀⢉⠤⢽⡈⣳⡄"
echo "⠀⠙⢳⠆⠄⡀⠀⠀⠀⣀⣁⠀⢸⢾⡁⠀"
echo "⠀⠀⠙⠛⣷⣣⠠⠎⠀⣠⠔⠉⣼⠏⠁⠀"
echo "⠀⠀⠀⠀⠉⢉⣳⡤⠀⢀⣤⡞⠁⠀⠀⠀"
echo "⠀⠀⠀⡴⠋⠉⡑⠃⠒⠊⣌⠉⢳⡄⠀⠀"
echo "⠀⠀⠀⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠃⠀⠀ https://github.com/Rickidevs/RickShell "


spinner() {
  local pid=$!
  local delay=0.1
  local spinstr='|/-\'
  while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
    local temp=${spinstr#?}
    printf " [%c]  " "$spinstr"
    local spinstr=$temp${spinstr%"$temp"}
    sleep $delay
    printf "\b\b\b\b\b\b"
  done
  printf "    \b\b\b\b"
}

echo -e "${YELLOW}Installation Starting...${NC}"
sleep 1


if command -v python3 &>/dev/null; then
  echo -e "Python3 ${GREEN}is installed.${NC} ✔"
else
  echo -e "Python3 ${RED}is not installed.${NC} ${YELLOW}Installing...${NC}"
  sudo apt-get update
  sudo apt-get install -y python3
  echo -e "Python3 ${GREEN}has been installed.${NC} ✔"
fi
sleep 1


if command -v pip3 &>/dev/null; then
  echo -e "pip3 ${GREEN}is installed.${NC} ✔"
else
  echo -e "pip3 ${RED}is not installed.${NC} ${YELLOW}Installing...${NC}"
  sudo apt-get install -y python3-pip
  echo -e "pip3 ${GREEN}has been installed.${NC} ✔"
fi
sleep 1


libraries=("colorama" "argparse")

for lib in "${libraries[@]}"; do
  python3 -c "import ${lib}" 2>/dev/null
  if [ $? -eq 0 ]; then
    echo -e "${lib} ${GREEN}library is installed.${NC} ✔"
  else
    echo -e "${lib} ${RED}library is not installed.${NC} ${YELLOW}Installing...${NC}"
    pip3 install --user ${lib} &
    spinner
    echo -e "${lib} ${GREEN}library has been installed.${NC} ✔"
  fi
  sleep 1
done


files=("main.py" "Shell" "setup.sh")
missing=false

for file in "${files[@]}"; do
  if [ ! -e $file ]; then
    echo -e "${file} ${RED}is missing.${NC} ✘"
    missing=true
  else
    echo -e "${file} ${GREEN}is present.${NC} ✔"
  fi
  sleep 1
done

if $missing; then
  echo -e "${RED}Some files are missing, installation cannot proceed.${NC}"
  exit 1
fi

echo -e "${YELLOW}Transferring files to /opt/RickShell directory...${NC}"
if [ ! -d "/opt/RickShell" ]; then
  sudo mkdir -p /opt/RickShell
fi

if [ -e "/opt/RickShell/main.py" ] && [ -e "/opt/RickShell/Shell" ] && [ -e "/opt/RickShell/setup.sh" ]; then
  echo -e "Files already present in /opt/RickShell. ${GREEN}✔${NC}"
else
  sudo cp main.py /opt/RickShell/
  sudo cp -r Shell /opt/RickShell/
  sudo cp setup.sh /opt/RickShell/
  echo -e "Files transferred. ${GREEN}✔${NC}"
fi
sleep 1

if ! grep -q "/opt/RickShell" /etc/profile; then
    echo -e "${YELLOW}Adding /opt/RickShell to PATH...${NC}"
    echo 'export PATH=$PATH:/opt/RickShell' | sudo tee -a /etc/profile
    source /etc/profile
    echo -e "PATH updated. ${GREEN}✔${NC}"
else
    echo -e "PATH ${GREEN}already contains /opt/RickShell.${NC} ✔"
fi
sleep 1

echo -e "${YELLOW}Creating RickShell command...${NC}"
sudo tee /usr/local/bin/RickShell > /dev/null <<EOL
#!/bin/bash
python3 /opt/RickShell/main.py "\$@"
EOL
sudo chmod +x /usr/local/bin/RickShell
echo -e "RickShell command created. ${GREEN}✔${NC}"

echo -e "${GREEN}Installation complete. You can run the 'RickShell' command from anywhere.${NC}"


