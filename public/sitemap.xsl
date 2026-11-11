<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
                xmlns:sitemap="http://www.sitemaps.org/schemas/sitemap/0.9"
                xmlns:xhtml="http://www.w3.org/1999/xhtml"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml" lang="en">
      <head>
        <title>XML Sitemap | YT4MP3 Media Technologies</title>
        <meta charset="UTF-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <link rel="icon" type="image/x-icon" href="/favicon.ico"/>
        <style>
          * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
          }
          body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f8fafc;
            color: #1e293b;
            padding: 32px 20px;
            line-height: 1.5;
          }
          .container {
            max-width: 1200px;
            margin: 0 auto;
          }
          .header {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 28px 32px;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
          }
          .brand-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 16px;
            margin-bottom: 12px;
          }
          .logo-group {
            display: flex;
            align-items: center;
            gap: 12px;
          }
          .logo-badge {
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            color: #ffffff;
            font-weight: 800;
            font-size: 15px;
            letter-spacing: 0.5px;
            padding: 6px 14px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25);
          }
          .title {
            font-size: 24px;
            font-weight: 800;
            color: #0f172a;
          }
          .subtitle {
            font-size: 14px;
            color: #64748b;
            margin-top: 4px;
          }
          .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 14px;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #f1f5f9;
          }
          .stat-card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 12px 16px;
          }
          .stat-label {
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #64748b;
          }
          .stat-value {
            font-size: 20px;
            font-weight: 800;
            color: #0f172a;
            margin-top: 2px;
          }
          .stat-value.green {
            color: #059669;
          }
          .card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
          }
          .card-header {
            padding: 18px 24px;
            background: #ffffff;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            align-items: center;
            justify-content: space-between;
          }
          .card-title {
            font-size: 16px;
            font-weight: 700;
            color: #0f172a;
          }
          .card-badge {
            background: #eef2ff;
            color: #4f46e5;
            font-size: 12px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 20px;
            border: 1px solid #e0e7ff;
          }
          .table-wrapper {
            overflow-x: auto;
          }
          table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 13px;
          }
          th {
            background: #f8fafc;
            color: #475569;
            font-weight: 700;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: 12px 20px;
            border-bottom: 1px solid #e2e8f0;
          }
          td {
            padding: 14px 20px;
            border-bottom: 1px solid #f1f5f9;
            vertical-align: middle;
          }
          tr:hover td {
            background: #f8fafc;
          }
          tr:last-child td {
            border-bottom: none;
          }
          .col-num {
            width: 50px;
            color: #94a3b8;
            font-weight: 600;
            text-align: center;
          }
          .url-link {
            color: #4f46e5;
            text-decoration: none;
            font-weight: 600;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
            font-size: 13px;
            word-break: break-all;
            transition: color 0.15s ease;
          }
          .url-link:hover {
            color: #3730a3;
            text-decoration: underline;
          }
          .badge-date {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: #ecfdf5;
            color: #047857;
            font-size: 12px;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 6px;
            border: 1px solid #a7f3d0;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
          }
          .badge-alt {
            display: inline-flex;
            align-items: center;
            background: #f1f5f9;
            color: #475569;
            font-size: 11px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
          }
          .footer {
            margin-top: 24px;
            text-align: center;
            font-size: 12px;
            color: #94a3b8;
          }
          .footer a {
            color: #64748b;
            text-decoration: none;
            font-weight: 600;
          }
          .footer a:hover {
            color: #4f46e5;
            text-decoration: underline;
          }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <div class="brand-row">
              <div class="logo-group">
                <span class="logo-badge">YT4MP3</span>
                <div>
                  <h1 class="title">XML Sitemap</h1>
                  <p class="subtitle">Search Engine Index Protocol • Clean, Valid &amp; Standardized for Crawlers</p>
                </div>
              </div>
              <a href="https://www.yt4mp3.com/" class="url-link" style="font-size: 13px;">Return to YT4MP3.com &#8594;</a>
            </div>
            <div class="stats-grid">
              <div class="stat-card">
                <div class="stat-label">Total URLs</div>
                <div class="stat-value">
                  <xsl:value-of select="count(sitemap:urlset/sitemap:url)"/>
                </div>
              </div>
              <div class="stat-card">
                <div class="stat-label">Languages</div>
                <div class="stat-value">15 + Default</div>
              </div>
              <div class="stat-card">
                <div class="stat-label">Last Updated</div>
                <div class="stat-value">
                  <xsl:value-of select="sitemap:urlset/sitemap:url[1]/sitemap:lastmod"/>
                </div>
              </div>
              <div class="stat-card">
                <div class="stat-label">Index Status</div>
                <div class="stat-value green">&#10003; 100% Ready</div>
              </div>
            </div>
          </div>

          <div class="card">
            <div class="card-header">
              <div class="card-title">Indexed URL Index</div>
              <span class="card-badge"><xsl:value-of select="count(sitemap:urlset/sitemap:url)"/> Entries</span>
            </div>
            <div class="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th class="col-num">#</th>
                    <th>Page URL</th>
                    <th>Last Modified</th>
                    <th>Alternates</th>
                  </tr>
                </thead>
                <tbody>
                  <xsl:for-each select="sitemap:urlset/sitemap:url">
                    <tr>
                      <td class="col-num"><xsl:value-of select="position()"/></td>
                      <td>
                        <a class="url-link" href="{sitemap:loc}">
                          <xsl:value-of select="sitemap:loc"/>
                        </a>
                      </td>
                      <td>
                        <span class="badge-date">
                          &#9679; <xsl:value-of select="sitemap:lastmod"/>
                        </span>
                      </td>
                      <td>
                        <span class="badge-alt">
                          <xsl:value-of select="count(xhtml:link)"/> hreflang
                        </span>
                      </td>
                    </tr>
                  </xsl:for-each>
                </tbody>
              </table>
            </div>
          </div>

          <div class="footer">
            <p>Generated by <a href="https://www.yt4mp3.com/">YT4MP3</a> Media Technologies &#8226; Powered by Google &amp; Bing Sitemap 0.9 Protocol</p>
          </div>
        </div>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
