// Serves a guide HTML file from Drive as an internal web app.
// Deploy: Deploy → New deployment → Web app. Execute as: Me. Who has access: Only myself (test), then Anyone within <your organization>.
const FILE_ID = 'paste-the-drive-file-id-here';
const TITLE = 'Product & Engineering Guide';

function doGet() {
  const html = DriveApp.getFileById(FILE_ID).getBlob().getDataAsString('UTF-8');
  return HtmlService.createHtmlOutput(html)
    .setTitle(TITLE)
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}
