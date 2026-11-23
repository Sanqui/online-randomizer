#!/bin/bash
cd ~/infra/ansible
ansible-playbook -i hosts.yml randomizer.yml -bK
