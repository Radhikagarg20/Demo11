$(document).ready(function () {
    $('#scraper-form').on('submit', function (e) {
        e.preventDefault();

        const url = $('#url').val();
        const dataType = $('#data_type').val();
        $('#result-data').text('Loading...');

        $.ajax({
            url: '/scrape',
            method: 'POST',
            data: {
                url: url,
                data_type: dataType
            },
            success: function (response) {
                const formattedList = generateBulletList(response);
                $('#result-data').html(formattedList);
            },
            error: function (err) {
                $('#result-data').text('Error: ' + err.responseText);
            }
        });

        function generateBulletList(obj) {
            let html = '<ul style="list-style-type: disc;">';
            for (const key in obj) {
                if (key === 'published_at') continue;
                if (Array.isArray(obj[key])) {
                    html += `<li><strong>${capitalizeKey(key)}:</strong><br>${formatArray(obj[key])}</li>`;
                } else if (typeof obj[key] === 'object' && obj[key] !== null) {
                    html += `<li><strong>${capitalizeKey(key)}:</strong> ${formatInlineObject(obj[key])}</li>`;
                } else {
                    html += `<li><strong>${capitalizeKey(key)}:</strong> ${obj[key]}</li>`;
                }
            }
            html += '</ul>';
            return html;
        }

        function capitalizeKey(key) {
            if (key === 'author') return 'Author';
            if (key === 'text') return 'Comment';
            return key.charAt(0).toUpperCase() + key.slice(1);
        }

        function formatArray(arr) {
            return arr
                .map((item) => {
                    if (typeof item === 'object') {
                        return formatInlineObject(item);
                    }
                    return item;
                })
                .join('<br>');
        }

        function formatInlineObject(obj) {
            return Object.entries(obj)
                .map(([key, value]) => `<strong>${capitalizeKey(key)}:</strong> ${value}`)
                .join(', ');
        }
    });
});
