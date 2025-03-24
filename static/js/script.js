// Single function to handle both types of video processing actions
function processVideo(actionType) {
    let url;
    let fetchOptions;

    // Get loader and output elements
    const loader = document.getElementById('loader');
    const output = document.getElementById('json-output');

    // Show the loader and clear previous output
    loader.style.display = 'block';
    output.textContent = '';

    // Determine URL and method based on actionType
    if (actionType === 'segments' || actionType === 'summary') {
        url = `/process_video`;
        fetchOptions = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `action=${actionType}`
        };
    } else {
        url = `/process/${actionType}`;
        fetchOptions = { method: 'POST' };
    }

    fetch(url, fetchOptions)
        .then(response => response.json())
        .then(data => {
            // Hide loader after response is received
            loader.style.display = 'none';

            if (data.success === false) {
                alert('Error processing video: ' + data.message);
            } else if (actionType === 'segments') {
                // Display segments in a table
                displaySegmentsTable(data.data, output);
            } else if (actionType === 'summary') {
                // Display summary in a modern layout
                displaySummary(data.data, output);
            } else {
                window.location.href = `/result/${actionType}`;
            }
        })
        .catch(error => {
            // Hide loader on error
            loader.style.display = 'none';
            console.error('Error:', error);
            alert('An error occurred while processing the video.');
        });
}

// Helper function to display segments in a table
function displaySegmentsTable(segments, outputElement) {
    // Clear the output element
    outputElement.innerHTML = '';

    // Create a table element
    const table = document.createElement('table');
    // Add a class for styling
    table.classList.add('modern-table');

    // Create table header
    const headerRow = document.createElement('tr');
    // Fields from JSON data
    const headers = ['Title', 'Timestamps', 'Description', 'Transcription'];
    headers.forEach(headerText => {
        const header = document.createElement('th');
        header.textContent = headerText;
        headerRow.appendChild(header);
    });
    table.appendChild(headerRow);

    // Populate table rows with segment data
    segments.forEach(segment => {
        const row = document.createElement('tr');

        // Add Title
        const titleCell = document.createElement('td');
        titleCell.textContent = segment.Title;
        row.appendChild(titleCell);

        // Add Timestamps
        const timestampsCell = document.createElement('td');
        timestampsCell.textContent = segment.Timestamps;
        row.appendChild(timestampsCell);

        // Add Description
        const descriptionCell = document.createElement('td');
        descriptionCell.textContent = segment.Description;
        row.appendChild(descriptionCell);

        // Add Transcription
        const transcriptionCell = document.createElement('td');
        transcriptionCell.textContent = segment.Transcription;
        row.appendChild(transcriptionCell);

        table.appendChild(row);
    });

    // Append the table to the output element
    outputElement.appendChild(table);

    // Add CSS styles for the modern table
    const style = document.createElement('style');
    style.textContent = `
        .modern-table {
            width: 100%;
            border-collapse: collapse;
            font-family: Arial, sans-serif;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            overflow: hidden;
        }
        .modern-table th, .modern-table td {
            padding: 12px 15px;
            text-align: left;
        }
        .modern-table th {
            background-color: #007BFF;
            color: white;
            font-weight: bold;
            text-transform: uppercase;
        }
        .modern-table tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .modern-table tr:hover {
            background-color: #e9ecef;
        }
        .modern-table td {
            border-bottom: 1px solid #ddd;
        }
        .modern-table tr:last-child td {
            border-bottom: none;
        }
    `;
    document.head.appendChild(style);
}

// Helper function to display summary in a modern layout
function displaySummary(summaryData, outputElement) {
    // Clear the output element
    outputElement.innerHTML = '';

    // Create a container for the summary
    const summaryContainer = document.createElement('div');
    summaryContainer.classList.add('summary-container');

    // Add Title
    const title = document.createElement('h2');
    title.textContent = summaryData.Title;
    title.classList.add('summary-title');
    summaryContainer.appendChild(title);

    // Add Duration
    const duration = document.createElement('p');
    duration.textContent = `Duration: ${summaryData.Duration}`;
    duration.classList.add('summary-duration');
    summaryContainer.appendChild(duration);

    // Add Keywords
    const keywordsTitle = document.createElement('h3');
    keywordsTitle.textContent = 'Keywords';
    keywordsTitle.classList.add('summary-subtitle');
    summaryContainer.appendChild(keywordsTitle);

    const keywordsList = document.createElement('ul');
    keywordsList.classList.add('summary-keywords');
    summaryData.Keywords.forEach(keyword => {
        const keywordItem = document.createElement('li');
        keywordItem.textContent = keyword;
        keywordsList.appendChild(keywordItem);
    });
    summaryContainer.appendChild(keywordsList);

    // Add Main Points
    const mainPointsTitle = document.createElement('h3');
    mainPointsTitle.textContent = 'Main Points';
    mainPointsTitle.classList.add('summary-subtitle');
    summaryContainer.appendChild(mainPointsTitle);

    const mainPointsList = document.createElement('ol');
    mainPointsList.classList.add('summary-main-points');
    summaryData.MainPoints.forEach(point => {
        const pointItem = document.createElement('li');
        pointItem.textContent = point;
        mainPointsList.appendChild(pointItem);
    });
    summaryContainer.appendChild(mainPointsList);

    // Add Summary
    const summaryText = document.createElement('p');
    summaryText.textContent = summaryData.Summary;
    summaryText.classList.add('summary-text');
    summaryContainer.appendChild(summaryText);

    // Append the summary container to the output element
    outputElement.appendChild(summaryContainer);

    // Add CSS styles for the modern summary layout
    const style = document.createElement('style');
    style.textContent = `
        .summary-container {
            font-family: Arial, sans-serif;
            background-color: #ffffff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            max-width: 800px;
            margin: 0 auto;
        }
        .summary-title {
            color: #007BFF;
            font-size: 24px;
            margin-bottom: 10px;
        }
        .summary-duration {
            color: #666;
            font-size: 14px;
            margin-bottom: 20px;
        }
        .summary-subtitle {
            color: #333;
            font-size: 18px;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        .summary-keywords {
            list-style-type: none;
            padding: 0;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 20px;
        }
        .summary-keywords li {
            background-color: #e9ecef;
            padding: 6px 12px;
            border-radius: 16px;
            font-size: 14px;
            color: #333;
        }
        .summary-main-points {
            padding-left: 20px;
            margin-bottom: 20px;
        }
        .summary-main-points li {
            margin-bottom: 8px;
            font-size: 14px;
            color: #555;
        }
        .summary-text {
            font-size: 16px;
            line-height: 1.6;
            color: #333;
        }
    `;
    document.head.appendChild(style);
}