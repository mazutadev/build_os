from rich.console import Console
from rich.table import Table
import time
from modules.command_executor import CommandExecutor

console = Console()
executer = CommandExecutor(use_sudo=True, debug=True)

def list_disks():
    console.print('[cyan]Достпные диски:[/cyan]')
    output = executer.run('lsblk -o NAME,SIZE,TYPE,MOUNTPOINT -d -n')

    if not output:
        console.print('[red]Не удалось получить список дисков![/red]')
        return
    
    table = Table(title='Список доступных дисков')
    table.add_column('Устройство', justify='left', style='green')
    table.add_column('Размер', justify='right', style='yellow')
    table.add_column('Тип', justify='left', style='cyan')

    for line in output.splitlines():
        cols = line.split()
        if "disk" in cols:
            table.add_row(f'/dev/{cols[0]}', cols[1], cols[2])

    console.print(table)

def prepare_usb(disk):
    confirm = console.input(f'[bold red]Выбран диск {disk}. Все данные будут удалены! Продолжить? (yes/no): [/bold red]')
    
    if confirm.lower() != 'yes':
        console.print('[yellow]Отмена операции.[/yellow]')
        return
    
    console.print('[cyan]Шаг 1: Очистка флешки и создание GPT-разметки[/cyan]]')
    executer.run(f'parted -s {disk} mklabel gpt')

    console.print('[cyan]Шаг 2: Создание разделов[/cyan]')
    executer.run(f'parted -s {disk} mkpart primary fat32 1MiB 513MiB')
    executer.run('partprobe')
    time.sleep(1)
    executer.run(f'parted -s {disk} set 1 esp on')
    executer.run(f'parted -s {disk} mkpart primary ext4 513MiB 16GB')
    executer.run(f'parted -s {disk} mkpart primary ext4 16GB 100%')

    console.print('[cyan]Шаг 3: Форматирование разделов[/cyan]')
    executer.run('partprobe')
    time.sleep(2)
    executer.run(f'mkfs.vfat -I -F32 {disk}1 -n EFI')
    executer.run(f'mkfs.ext4 -F {disk}2 -L LIVE_USB')
    executer.run(f'mkfs.ext4 -F {disk}3 -L casper-rw')

    console.print('[bold green]Флешка успешно подготовлена![/bold green]')

def unmount_partitions(disk):
    console.print(f'[yellow]Отмонтирование разделов на {disk}...[/yellow]')
    partitions = executer.run(f'lsblk -lno NAME,MOUNTPOINT | grep "^$(basename {disk})[0-9])" | awk "{{print $1}}"')
    print(partitions)

    if partitions:
        for part in partitions.splitlines():
            part_path = f'/dev/{part}'
            executer.run(f'sudo umount {part_path}')
            console.print(f'[green]Отмонтирован:[/green] {part_path}')
    else:
        console.print(f'[yellow]Разделы не были смонтированы.[/yellow]')
