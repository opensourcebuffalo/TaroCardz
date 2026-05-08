<?php
// index.php
$jsonPath = __DIR__ . '/meeting_3347.json';

if (!file_exists($jsonPath)) {
    die("Missing meeting_3347.json. Put your scraper JSON file in the same folder as this PHP file.");
}

$data = json_decode(file_get_contents($jsonPath), true);

if (!$data || !isset($data['items'])) {
    die("Could not read agenda items from meeting_3347.json.");
}

$items = $data['items'];

function h($value) {
    return htmlspecialchars($value ?? '', ENT_QUOTES, 'UTF-8');
}

function cardType($title, $department) {
    $t = strtolower($title . ' ' . $department);

    if (str_contains($t, 'budget') || str_contains($t, 'finance')) return 'THE BUDGET';
    if (str_contains($t, 'appointment') || str_contains($t, 'appoint')) return 'THE APPOINTMENT';
    if (str_contains($t, 'contract') || str_contains($t, 'agreement') || str_contains($t, 'lease')) return 'THE CONTRACT';
    if (str_contains($t, 'change order')) return 'THE CHANGE ORDER';
    if (str_contains($t, 'zoning') || str_contains($t, 'variance')) return 'THE VARIANCE';
    if (str_contains($t, 'permit') || str_contains($t, 'license')) return 'THE PERMIT';
    if (str_contains($t, 'police')) return 'THE WATCH';
    if (str_contains($t, 'public works') || str_contains($t, 'street') || str_contains($t, 'water')) return 'THE WORKS';

    return 'THE ITEM';
}

function taroSez($title, $department) {
    $t = strtolower($title);

    if (str_contains($t, 'change order')) {
        return "This item changes the cost or terms of an existing city project.";
    }

    if (str_contains($t, 'appointment') || str_contains($t, 'appoint')) {
        return "This item places or changes a person in a city government role.";
    }

    if (str_contains($t, 'lease') || str_contains($t, 'agreement')) {
        return "This item asks Council to approve an agreement involving city property, services, or partners.";
    }

    if (str_contains($t, 'license') || str_contains($t, 'permit')) {
        return "This item involves permission to operate, build, sell, or use property in the city.";
    }

    if (str_contains($t, 'report')) {
        return "This item submits a report for Council review.";
    }

    return "This agenda item is before City Hall and may affect public resources, services, or neighborhood conditions.";
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>TaroCardz — Swipe Through City Hall</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <style>
        body {
            margin: 0;
            font-family: Georgia, serif;
            background: #f3e8c9;
            color: #111;
            overflow-x: hidden;
        }

        header {
            text-align: center;
            padding: 24px 16px 10px;
        }

        header h1 {
            margin: 0;
            font-size: 2.2rem;
            letter-spacing: 1px;
        }

        header p {
            margin: 8px 0 0;
            font-family: Arial, sans-serif;
            font-size: 1rem;
        }

        .deck {
            position: relative;
            width: 92%;
            max-width: 420px;
            height: 640px;
            margin: 20px auto;
        }

        .card {
            position: absolute;
            inset: 0;
            background: #fff7dc;
            border: 5px solid #0b3d91;
            border-radius: 24px;
            box-shadow: 0 15px 40px rgba(0,0,0,.25);
            padding: 22px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform .25s ease, opacity .25s ease;
            touch-action: pan-y;
        }

        .card.red {
            border-color: #b51d1a;
        }

        .card.gold {
            border-color: #d9a441;
        }

        .roman {
            text-align: center;
            font-size: 1rem;
            font-weight: bold;
            color: #b51d1a;
        }

        .type {
            text-align: center;
            font-size: 1.9rem;
            font-weight: bold;
            border-top: 2px solid #111;
            border-bottom: 2px solid #111;
            padding: 10px 0;
            margin: 8px 0 12px;
        }

        .item-number {
            text-align: center;
            font-family: Arial, sans-serif;
            font-weight: bold;
            color: #0b3d91;
            margin-bottom: 12px;
        }

        .title {
            font-size: 1.25rem;
            line-height: 1.25;
            text-align: center;
            margin: 10px 0;
        }

        .meta {
            font-family: Arial, sans-serif;
            background: #0b3d91;
            color: white;
            padding: 10px;
            border-radius: 12px;
            text-align: center;
            font-size: .9rem;
        }

        .sez {
            font-family: Arial, sans-serif;
            background: #f7d45c;
            padding: 14px;
            border-radius: 12px;
            line-height: 1.35;
            margin-top: 14px;
        }

        .actions {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            font-family: Arial, sans-serif;
        }

        button, a.button {
            border: none;
            padding: 12px;
            border-radius: 12px;
            font-weight: bold;
            cursor: pointer;
            text-decoration: none;
            text-align: center;
            color: white;
            background: #b51d1a;
        }

        a.button.blue {
            background: #0b3d91;
        }

        .controls {
            text-align: center;
            margin: 10px auto 30px;
            font-family: Arial, sans-serif;
        }

        .controls button {
            margin: 4px;
            width: 120px;
        }

        .counter {
            text-align: center;
            font-family: Arial, sans-serif;
            font-weight: bold;
        }

        .hidden {
            display: none;
        }
    </style>
</head>

<body>

<header>
    <h1>Taro Sez...</h1>
    <p>Swipe Through City Hall</p>
</header>

<div class="counter">
    <span id="currentIndex">1</span> / <?= count($items) ?> cards
</div>

<div class="deck" id="deck">
    <?php foreach (array_reverse($items) as $index => $item): 
        $title = $item['title'] ?? '';
        $department = $item['display_section'] ?? $item['department'] ?? '';
        $type = cardType($title, $department);
        $sez = taroSez($title, $department);
        $fileNumber = $item['file_number'] ?? 'No File #';
        $itemUrl = $item['item_url'] ?? '#';
        $attachmentCount = count($item['attachments'] ?? []);
        $colorClass = $index % 3 === 0 ? 'red' : ($index % 3 === 1 ? 'gold' : '');
    ?>
        <div class="card <?= $colorClass ?>">
            <div>
                <div class="roman">TAROCARDZ</div>
                <div class="type"><?= h($type) ?></div>
                <div class="item-number"><?= h($fileNumber) ?></div>

                <div class="title">
                    <?= h($title) ?>
                </div>

                <div class="meta">
                    <?= h($department) ?><br>
                    <?= h($data['meeting_date'] ?? '') ?><br>
                    <?= $attachmentCount ?> source document<?= $attachmentCount === 1 ? '' : 's' ?>
                </div>

                <div class="sez">
                    <strong>Taro Sez:</strong><br>
                    <?= h($sez) ?>
                </div>
            </div>

            <div class="actions">
                <button onclick="swipeCard('left')">Pass</button>
                <button onclick="swipeCard('right')">Follow</button>
                <a class="button blue" href="<?= h($itemUrl) ?>" target="_blank">View Item</a>
                <button onclick="shareCard('<?= h($fileNumber) ?>', '<?= h($title) ?>')">Share</button>
            </div>
        </div>
    <?php endforeach; ?>
</div>

<div class="controls">
    <button onclick="swipeCard('left')">← Pass</button>
    <button onclick="swipeCard('right')">Follow →</button>
</div>

<script>
let cards = Array.from(document.querySelectorAll('.card'));
let current = cards.length - 1;
let total = cards.length;

function updateCounter() {
    let viewed = total - current;
    if (viewed < 1) viewed = total;
    document.getElementById('currentIndex').innerText = Math.min(viewed, total);
}

function swipeCard(direction) {
    if (current < 0) return;

    const card = cards[current];

    if (direction === 'right') {
        card.style.transform = 'translateX(140%) rotate(18deg)';
    } else {
        card.style.transform = 'translateX(-140%) rotate(-18deg)';
    }

    card.style.opacity = '0';

    current--;
    updateCounter();

    if (current < 0) {
        setTimeout(() => {
            document.getElementById('deck').innerHTML = `
                <div class="card">
                    <div>
                        <div class="roman">THE END</div>
                        <div class="type">CITY HALL READ</div>
                        <div class="title">You made it through the agenda.</div>
                        <div class="sez"><strong>Taro Sez:</strong><br>Democracy is procedural. Stay weird. Stay informed.</div>
                    </div>
                    <div class="actions">
                        <button onclick="location.reload()">Restart Deck</button>
                    </div>
                </div>
            `;
        }, 300);
    }
}

function shareCard(fileNumber, title) {
    const text = `Taro Sez: ${fileNumber} — ${title}`;
    const url = window.location.href;

    if (navigator.share) {
        navigator.share({
            title: 'TaroCardz',
            text: text,
            url: url
        });
    } else {
        navigator.clipboard.writeText(`${text} ${url}`);
        alert('Card copied to clipboard.');
    }
}

let startX = 0;

document.addEventListener('touchstart', e => {
    startX = e.touches[0].clientX;
});

document.addEventListener('touchend', e => {
    let endX = e.changedTouches[0].clientX;
    let diff = endX - startX;

    if (Math.abs(diff) > 80) {
        swipeCard(diff > 0 ? 'right' : 'left');
    }
});

updateCounter();
</script>

</body>
</html>
