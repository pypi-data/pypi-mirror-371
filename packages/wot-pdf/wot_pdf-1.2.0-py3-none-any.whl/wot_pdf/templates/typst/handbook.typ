// 📖 HANDBOOK/MANUAL TEMPLATE
// ===========================
// Professional manual and handbook layout

#let handbook-template(
  title: "Handbook Title",
  subtitle: none,
  version: none,
  company: none,
  author: none,
  date: none,
  body
) = {
  
  // ===== HANDBOOK COLOR SCHEME =====
  let primary-color = rgb("#2e7d32")       // Forest green
  let secondary-color = rgb("#795548")     // Brown
  let accent-color = rgb("#ff8f00")        // Amber
  let warning-color = rgb("#d32f2f")       // Red
  let info-color = rgb("#1976d2")          // Blue
  let dark-color = rgb("#424242")          // Dark gray
  let light-bg = rgb("#f8f9fa")            // Light background
  let section-bg = rgb("#e8f5e8")          // Light green

  // ===== PAGE SETUP =====
  set page(
    paper: "a4",
    margin: (
      top: 2.5cm,
      bottom: 2cm,
      left: 2.5cm,
      right: 2cm
    ),
    header: context {
      if counter(page).get().first() > 1 [
        #line(length: 100%, stroke: 2pt + primary-color)
        #v(-1em)
        #grid(
          columns: (1fr, auto, 1fr),
          inset: (top: 0.5em),
          align: (left, center, right),
          
          // Left: Chapter info
          text(size: 9pt, fill: dark-color.lighten(30%))[
            #context {
              let headings = query(heading.where(level: 1))
              if headings.len() > 0 {
                let current = headings.last()
                upper(current.body)
              }
            }
          ],
          
          // Center: Company/Title
          text(size: 10pt, weight: "bold", fill: primary-color)[
            #if company != none [#company] else [#title]
          ],
          
          // Right: Page number
          text(size: 9pt, fill: dark-color.lighten(30%))[
            Page #counter(page).display()
          ]
        )
      ]
    },
    footer: context {
      if counter(page).get().first() > 1 [
        #line(length: 100%, stroke: 1pt + primary-color.lighten(50%))
        #v(0.3em)
        #grid(
          columns: (1fr, auto, 1fr),
          align: (left, center, right),
          
          text(size: 8pt, fill: dark-color.lighten(50%))[
            #if version != none [Version #version] else []
          ],
          
          text(size: 8pt, fill: dark-color.lighten(50%))[
            #if date != none [#date] else []
          ],
          
          text(size: 8pt, fill: dark-color.lighten(50%))[
            #if author != none [#author] else []
          ]
        )
      ]
    }
  )

  // ===== TYPOGRAPHY =====
  set text(
    font: ("Source Sans Pro", "Segoe UI", "sans-serif"),
    size: 11pt,
    fill: dark-color,
    lang: "en"
  )

  set par(
    justify: true,
    leading: 0.7em,
    first-line-indent: 1.2em
  )

  // ===== COVER PAGE =====
  if title != none [
    #rect(
      width: 100%,
      height: 100%,
      fill: gradient.linear(
        angle: 135deg,
        primary-color,
        primary-color.lighten(30%)
      ),
      radius: 12pt
    )[
      #place(
        top + left,
        dx: 3em,
        dy: 3em,
        rect(
          width: 80%,
          fill: rgba(255, 255, 255, 0.95),
          stroke: 2pt + white,
          radius: 8pt,
          inset: 3em
        )[
          // Company logo area
          #if company != none [
            #align(center)[
              #rect(
                width: 8em,
                height: 3em,
                fill: primary-color.lighten(90%),
                stroke: 2pt + primary-color,
                radius: 6pt
              )[
                #align(center + horizon)[
                  #text(
                    size: 16pt,
                    weight: "bold",
                    fill: primary-color
                  )[#company]
                ]
              ]
            ]
            #v(3em)
          ]
          
          // Main title
          #align(center)[
            #text(
              size: 32pt,
              weight: "bold",
              fill: primary-color
            )[#title]
          ]
          
          #if subtitle != none [
            #v(1em)
            #align(center)[
              #text(
                size: 18pt,
                fill: secondary-color,
                style: "italic"
              )[#subtitle]
            ]
          ]
          
          #v(4em)
          
          // Handbook info box
          #rect(
            width: 100%,
            fill: light-bg,
            stroke: 2pt + primary-color.lighten(50%),
            inset: 2em,
            radius: 8pt
          )[
            #set text(size: 14pt)
            #grid(
              columns: (auto, 1fr),
              row-gutter: 1em,
              column-gutter: 2em,
              align: (right, left),
              
              if version != none [
                text(weight: "bold", fill: primary-color)[Version:],
                text(fill: dark-color)[#version]
              ],
              
              if author != none [
                text(weight: "bold", fill: primary-color)[Author:],
                text(fill: dark-color)[#author]
              ],
              
              if date != none [
                text(weight: "bold", fill: primary-color)[Date:],
                text(fill: dark-color)[#date]
              ]
            )
          ]
        ]
      )
    ]
    
    #pagebreak()
  ]

  // ===== HANDBOOK HEADINGS =====
  show heading.where(level: 1): it => [
    #pagebreak(weak: true)
    #v(2em)
    
    // Chapter number and title
    #rect(
      width: 100%,
      height: 4em,
      fill: gradient.linear(
        angle: 90deg,
        primary-color,
        primary-color.lighten(20%)
      ),
      radius: 8pt
    )[
      #grid(
        columns: (auto, 1fr),
        align: (center, left),
        inset: (x: 2em, y: 0em),
        
        // Chapter number
        circle(
          radius: 1.5em,
          fill: white,
          stroke: 3pt + primary-color
        )[
          #align(center + horizon)[
            #text(
              size: 20pt,
              weight: "bold",
              fill: primary-color
            )[
              #counter(heading).display()
            ]
          ]
        ],
        
        // Chapter title
        align(left + horizon)[
          #text(
            size: 24pt,
            weight: "bold",
            fill: white
          )[#it.body]
        ]
      )
    ]
    
    #v(2em)
  ]

  show heading.where(level: 2): it => [
    #v(2em)
    #rect(
      width: 100%,
      fill: section-bg,
      stroke: (left: 6pt + secondary-color),
      inset: (x: 2em, y: 1.2em),
      radius: (right: 8pt)
    )[
      #grid(
        columns: (auto, 1fr),
        gutter: 1.5em,
        align: (center, left),
        
        // Section number
        rect(
          width: 3em,
          height: 2em,
          fill: secondary-color,
          radius: 4pt
        )[
          #align(center + horizon)[
            #text(
              size: 14pt,
              weight: "bold",
              fill: white
            )[
              #counter(heading).display()
            ]
          ]
        ],
        
        // Section title
        text(
          size: 18pt,
          weight: "bold",
          fill: secondary-color
        )[#it.body]
      )
    ]
    #v(1.5em)
  ]

  show heading.where(level: 3): it => [
    #v(1.5em)
    #grid(
      columns: (auto, 1fr),
      gutter: 1em,
      align: (center, left),
      
      text(
        size: 16pt,
        weight: "bold",
        fill: accent-color
      )[●],
      
      text(
        size: 16pt,
        weight: "bold",
        fill: accent-color
      )[#it.body]
    )
    #v(1em)
  ]

  // ===== HANDBOOK LISTS =====
  show list: it => [
    #v(1em)
    #set list(
      marker: rect(
        width: 0.6em,
        height: 0.6em,
        fill: primary-color,
        radius: 2pt
      )
    )
    #it
    #v(0.8em)
  ]

  show enum: it => [
    #v(1em)
    #set enum(numbering: n => rect(
      width: 1.8em,
      height: 1.8em,
      fill: gradient.radial(
        primary-color,
        primary-color.lighten(20%)
      ),
      radius: 4pt
    )[
      #align(center + horizon)[
        #text(
          size: 11pt,
          weight: "bold",
          fill: white
        )[#n]
      ]
    ])
    #it
    #v(0.8em)
  ]

  // ===== CODE BLOCKS =====
  show raw.where(block: true): it => [
    #v(1.5em)
    #rect(
      width: 100%,
      fill: dark-color.lighten(97%),
      stroke: 2pt + dark-color.lighten(80%),
      radius: 6pt,
      inset: 1.5em
    )[
      #place(
        top + right,
        dx: -1em,
        dy: -1em,
        rect(
          fill: info-color,
          radius: (top-right: 4pt, bottom-left: 4pt),
          inset: (x: 8pt, y: 4pt)
        )[
          #text(size: 9pt, fill: white, weight: "bold")[CODE]
        ]
      )
      #set text(
        font: ("Fira Code", "Consolas", "monospace"),
        size: 10pt,
        fill: dark-color
      )
      #it
    ]
    #v(1.2em)
  ]

  // ===== INLINE CODE =====
  show raw.where(block: false): it => [
    #rect(
      fill: info-color.lighten(95%),
      stroke: 1pt + info-color.lighten(70%),
      outset: (x: 4pt, y: 2pt),
      radius: 3pt
    )[
      #text(
        font: ("Fira Code", "Consolas", "monospace"),
        size: 0.9em,
        fill: info-color.darken(20%)
      )[#it]
    ]
  ]

  // ===== CALLOUT BOXES =====
  show quote: it => [
    #v(1.5em)
    #rect(
      width: 100%,
      fill: gradient.linear(
        angle: 45deg,
        accent-color.lighten(95%),
        accent-color.lighten(98%)
      ),
      stroke: (left: 8pt + accent-color),
      inset: (x: 2em, y: 1.5em),
      radius: (right: 8pt)
    )[
      #place(
        top + left,
        dx: -2.5em,
        dy: -0.8em,
        circle(
          radius: 12pt,
          fill: accent-color
        )[
          #align(center + horizon)[
            #text(size: 14pt, fill: white, weight: "bold")[ⓘ]
          ]
        ]
      )
      
      #set text(size: 12pt, fill: accent-color.darken(30%))
      #text(weight: "bold", size: 13pt)[Note: ]
      #it.body
    ]
    #v(1.2em)
  ]

  // ===== WARNING BOXES =====
  let warning-box(content) = [
    #v(1.5em)
    #rect(
      width: 100%,
      fill: warning-color.lighten(95%),
      stroke: 2pt + warning-color,
      inset: 2em,
      radius: 8pt
    )[
      #place(
        top + left,
        dx: -2.5em,
        dy: -1em,
        rect(
          fill: warning-color,
          radius: 4pt,
          inset: 8pt
        )[
          #text(size: 16pt, fill: white, weight: "bold")[⚠]
        ]
      )
      
      #text(weight: "bold", size: 13pt, fill: warning-color)[WARNING: ]
      #text(size: 12pt, fill: warning-color.darken(20%))[#content]
    ]
    #v(1.2em)
  ]

  // ===== TABLES =====
  set table(
    stroke: (x, y) => {
      if y == 0 { 2pt + primary-color }
      else { 1pt + primary-color.lighten(70%) }
    },
    fill: (x, y) => {
      if y == 0 { primary-color.lighten(90%) }
      else if calc.odd(y) { light-bg }
      else { white }
    },
    inset: 12pt
  )

  show table: it => [
    #v(1.5em)
    #rect(
      stroke: 2pt + primary-color.lighten(50%),
      radius: 8pt,
      inset: 0pt
    )[#it]
    #v(1em)
  ]

  // ===== FIGURES =====
  show figure: it => [
    #v(2em)
    #rect(
      width: 100%,
      stroke: 2pt + secondary-color.lighten(50%),
      fill: white,
      inset: 2em,
      radius: 8pt
    )[
      #align(center)[#it.body]
      
      #if it.caption != none [
        #v(1.5em)
        #rect(
          width: 100%,
          fill: secondary-color.lighten(95%),
          inset: 1.2em,
          radius: 4pt
        )[
          #set text(size: 11pt, fill: secondary-color.darken(20%))
          #align(center)[
            #text(weight: "bold")[Figure #counter(figure).display():] #it.caption
          ]
        ]
      ]
    ]
    #v(1.8em)
  ]

  // ===== EMPHASIS =====
  show strong: it => text(fill: primary-color, weight: "bold", size: 1.05em)[#it]
  show emph: it => text(fill: secondary-color, style: "italic")[#it]
  show link: it => text(fill: info-color, decoration: "underline")[#it]

  // ===== MAIN CONTENT =====
  body
}

// Default template call
#show: handbook-template.with(
  title: [HANDBOOK TEMPLATE],
  subtitle: [Professional Manual & Documentation],
  version: [1.0],
  company: [Organization Name],
  author: [Documentation Team],
  date: datetime.today().display("[day]. [month repr:long] [year]")
)
