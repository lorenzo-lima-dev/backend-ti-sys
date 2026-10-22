powershell.exe -ExecutionPolicy Bypass -Command "Invoke-Expression (Get-Content '%~f0' | Select-Object -Skip 5 | Out-String)"
goto :EOF

:POWERSHELL

$paths = @(
    "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*",
    "HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*",
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*"
)

$paths = @(
    "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*",
    "HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*",
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*"
)

$programas = Get-ItemProperty $paths -ErrorAction SilentlyContinue |
Where-Object { $_.DisplayName } |
Select-Object @{Name = 'nome_exibicao'; Expression = { $_.DisplayName } },
@{Name = 'versao'; Expression = { $_.DisplayVersion } },
@{Name = 'publicador'; Expression = { $_.Publisher } } |
Sort-Object nome_exibicao, versao, publicador -Unique

$monitores = Get-CimInstance -Namespace root\wmi -ClassName WmiMonitorID -ErrorAction SilentlyContinue |
ForEach-Object {
    [PSCustomObject]@{
        fabricante   = -join ($_.ManufacturerName | Where-Object { $_ -ne 0 } | ForEach-Object { [char]$_ })
        modelo       = -join ($_.UserFriendlyName | Where-Object { $_ -ne 0 } | ForEach-Object { [char]$_ })
        numero_serie = -join ($_.SerialNumberID   | Where-Object { $_ -ne 0 } | ForEach-Object { [char]$_ })
        ativo        = $_.Active
    }
}

$user = Get-CimInstance Win32_ComputerSystem
$os = Get-CimInstance Win32_OperatingSystem
$userAccount = Get-CimInstance Win32_UserAccount -Filter "LocalAccount=True" -ErrorAction SilentlyContinue

$usuariosLocais = $userAccount | Select-Object `
@{Name = 'nome'; Expression = { $_.Name } },
@{Name = 'nome_completo'; Expression = { $_.FullName } },
@{Name = 'desabilitado'; Expression = { $_.Disabled } },
@{Name = 'descricao'; Expression = { $_.Description } }

$gpus = Get-CimInstance Win32_VideoController -ErrorAction SilentlyContinue |
Select-Object `
@{Name = 'nome'; Expression = { $_.Name } },
@{Name = 'processador_video'; Expression = { $_.VideoProcessor } },
@{Name = 'vram_gb'; Expression = {
        if ($_.AdapterRAM -and $_.AdapterRAM -gt 0) {
            [math]::Round($_.AdapterRAM / 1GB, 2)
        }
        else { $null }
    }
},
@{Name = 'versao_driver'; Expression = { $_.DriverVersion } },
@{Name = 'data_driver'; Expression = {
        if ($_.DriverDate) { $_.DriverDate.ToString("o") } else { $null }
    }
},
@{Name = 'resolucao'; Expression = {
        if ($_.CurrentHorizontalResolution -and $_.CurrentVerticalResolution) {
            "$($_.CurrentHorizontalResolution) x $($_.CurrentVerticalResolution)"
        }
        else { $_.VideoModeDescription }
    }
},
@{Name = 'taxa_atualizacao'; Expression = { $_.CurrentRefreshRate } },
@{Name = 'status'; Expression = { $_.Status } }


$DDR = @{
    '20' = 'DDR'
    '21' = 'DDR2'
    '24' = 'DDR3'
    '26' = 'DDR4'
    '30' = 'LPDDR4'
    '34' = 'DDR5'
    '35' = 'LPDDR5'
}

$rams = @(Get-CimInstance Win32_PhysicalMemory -ErrorAction SilentlyContinue |
    Select-Object `
    @{Name = 'slot'; Expression = { $_.DeviceLocator } },
    @{Name = 'capacidade_gb'; Expression = {
            if ($_.Capacity) {
                [math]::Round($_.Capacity / 1GB, 2)
            }
            else {
                $null
            }
        }
    },
    @{Name = 'velocidade'; Expression = { $_.Speed } },
    @{Name = 'velocidade_configurada'; Expression = { $_.ConfiguredClockSpeed } },
    @{Name = 'tipo'; Expression = {
            $DDR[$_.SMBIOSMemoryType.ToString()]
        }
    }
)

$hd = Get-PhysicalDisk | ForEach-Object {
    $disk = $_

    $windowsDisk = Get-Disk | Where-Object {
        $_.FriendlyName -eq $disk.FriendlyName
    } | Select-Object -First 1

    $volumes = @()

    if ($windowsDisk) {
        $volumes = Get-Partition -DiskNumber $windowsDisk.Number -ErrorAction SilentlyContinue |
        Get-Volume -ErrorAction SilentlyContinue |
        Where-Object { $_.DriveLetter }
    }

    $totalSpace = 0
    $freeSpace = 0
    if ($volumes) {
        $totalSpace = ($volumes | Measure-Object Size -Sum).Sum
        $freeSpace = ($volumes | Measure-Object SizeRemaining -Sum).Sum
    }

    [PSCustomObject]@{
        modelo  = $disk.FriendlyName
        serial  = $disk.SerialNumber
        tipo    = $disk.MediaType
        tipoBus = $disk.BusType
        status  = $disk.HealthStatus
        total   = [math]::Round($disk.Size / 1GB, 2)
        livre   = [math]::Round($freeSpace / 1GB, 2)
        usado   = [math]::Round(($totalSpace - $freeSpace) / 1GB, 2)
        pUsado  = if ($totalSpace -and $totalSpace -gt 0) {
            [math]::Round((($totalSpace - $freeSpace) / $totalSpace) * 100, 2)
        }
        else {
            0
        }
    }
}

$cpuRaw = Get-CimInstance Win32_Processor | Select-Object -First 1
$cpu = [PSCustomObject]@{
    nome                  = $cpuRaw.Name
    fabricante            = $cpuRaw.Manufacturer
    nucleos               = $cpuRaw.NumberOfCores
    processadores_logicos = $cpuRaw.NumberOfLogicalProcessors
    clock_max_ghz         = [math]::Round($cpuRaw.MaxClockSpeed / 1000, 2)
    id_processador        = $cpuRaw.ProcessorId
    soquete               = $cpuRaw.SocketDesignation
}

$pc = Get-CimInstance Win32_ComputerSystem |
Select-Object Manufacturer, Model, SystemFamily

$placaMae = Get-CimInstance Win32_BaseBoard |
Select-Object Manufacturer, Product, SerialNumber

$conexoes = Get-CimInstance Win32_PnPEntity -ErrorAction SilentlyContinue |
Where-Object { $_.Status -eq "OK" } |
Select-Object `
@{Name = 'nome'; Expression = { $_.Name } },
@{Name = 'fabricante'; Expression = { $_.Manufacturer } },
@{Name = 'class_guid'; Expression = { $_.ClassGuid } },
@{Name = 'pnp_class'; Expression = { $_.PNPClass } },
@{Name = 'device_id'; Expression = { $_.DeviceID } },
@{Name = 'pnp_device_id'; Expression = { $_.PNPDeviceID } },
@{Name = 'status'; Expression = { $_.Status } } |
Sort-Object pnp_class, nome


$ipPublico = "Desconhecido"
try {
    $ipPublico = (Invoke-RestMethod -Uri "https://api.ipify.org" -TimeoutSec 5).Trim()
}
catch {
}

$ipsInternos = (
    Get-NetIPAddress -AddressFamily IPv4 |
    Where-Object {
        $_.PrefixOrigin -ne 'WellKnown'
    }
).IPAddress -join ' '

$payload = [PSCustomObject]@{
    nome_computador      = $user.Name
    dominio              = $user.Domain
    usuario_atual        = $user.UserName
    fabricante           = $pc.Manufacturer
    modelo               = $pc.Model
    familia_sistema      = $pc.SystemFamily
    placa_mae_fabricante = $placaMae.Manufacturer
    placa_mae_produto    = $placaMae.Product
    placa_mae_serial     = $placaMae.SerialNumber
    sistema_operacional  = $os.Caption
    versao_so            = $os.Version
    arquitetura          = $os.OSArchitecture
    ram                  = @($rams)
    memoria              = @($hd)

    ips_internos         = $ipsInternos
    ip_publico           = $ipPublico
    cpu                  = $cpu
    gpus                 = @($gpus)
    monitores            = @($monitores)
    programas            = @($programas)
    conexoes             = @($conexoes)
    usuarios_locais      = @($usuariosLocais)
}

$fastapiUrl = "http://192.168.0.208:8030/api/v1/inventario/"

$headers = @{
    "Content-Type" = "application/json"
}

$bodyObject = @{
    payload = $payload
}

$jsonBody = $bodyObject | ConvertTo-Json -Depth 20 -Compress

try {
    $response = Invoke-RestMethod `
        -Uri $fastapiUrl `
        -Method Post `
        -Headers $headers `
        -Body ([System.Text.Encoding]::UTF8.GetBytes($jsonBody)) `
        -ContentType "application/json; charset=utf-8"
}
catch {
    Write-Error "Você está fora da rede do servidor do agente!"
}