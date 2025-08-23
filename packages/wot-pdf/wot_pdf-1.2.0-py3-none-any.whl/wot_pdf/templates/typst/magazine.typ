// 📰 MAGAZINE STYLE TEMPLATE
// ===========================
// Publication-style layout with columns and magazine-like design

#let magazine-template(
  title: "Magazine Document",
  subtitle: none,
  author: none,
  date: none,
  body
) = {
  
  // ===== MAGAZINE COLOR SCHEME =====
  let primary-color = rgb("#d32f2f")       // Magazine red
  let secondary-color = rgb("#1976d2")     // Professional blue
  let accent-color = rgb("#ff6f00")        // Highlight orange
  let text-color = rgb("#212121")          // Dark text
  let light-bg = rgb("#fafafa")            // Light background
  let border-color = rgb("#e0e0e0")        // Borders

  // ===== PAGE SETUP =====
  set page(
    paper: "a4",
    margin: (
      top: 2cm,
      bottom: 2cm,
      left: 1.8cm,
      right: 1.8cm
    ),
    header: context {
      if counter(page).get().first() > 1 [
        #set text(size: 8pt, fill: primary-color, weight: "bold")
        #grid(
          columns: (1fr, auto, 1fr),
          align(left)[#title],
          circle(radius: 2pt, fill: primary-color),
          align(right)[PAGE #counter(page).display()]
        )
        #v(-0.5em)
        #line(length: 100%, stroke: 0.5pt + border-color)
      ]
    },
    footer: context {
      set text(size: 8pt, fill: text-color.lighten(40%))
      line(length: 100%, stroke: 0.5pt + border-color)
      v(-0.8em)
      align(center)[
        #datetime.today().display("[day]/[month]/[year]") • 
        #text(style: "italic")[WOT-PDF Magazine Engine]
      ]
    }
  )

  // ===== TYPOGRAPHY =====
  set text(
    font: ("Times New Roman", "Georgia", "serif"),
    size: 10.5pt,
    fill: text-color,
    lang: "en"
  )

  set par(
    justify: true,
    leading: 0.6em,
    first-line-indent: 1.2em
  )

  // ===== MAGAZINE TITLE LAYOUT =====
  if title != none [
    #rect(
      width: 100%,
      height: 3em,
      fill: primary-color,
      inset: 0pt
    )[
      #align(center + horizon)[
        #text(
          size: 32pt,
          weight: "bold",
          fill: white,
          font: ("Arial", "sans-serif")
        )[#title]
      ]
    ]
    
    #if subtitle != none [
      #v(0.5em)
      #align(center)[
        #rect(
          fill: light-bg,
          stroke: 1pt + border-color,
          inset: 1em,
          radius: 4pt
        )[
          #text(
            size: 14pt,
            style: "italic",
            fill: secondary-color,
            font: ("Arial", "sans-serif")
          )[#subtitle]
        ]
      ]
    ]
    
    #v(1em)
    
    // Magazine info bar
    #rect(
      width: 100%,
      height: 2em,
      fill: light-bg,
      stroke: (
        top: 1pt + border-color,
        bottom: 1pt + border-color
      ),
      inset: 0pt
    )[
      #set text(size: 9pt, fill: text-color.lighten(30%))
      #grid(
        columns: (1fr, auto, 1fr),
        inset: 0.5em,
        align(left + horizon)[
          #if author != none [*Editor:* #author]
        ],
        align(center + horizon)[
          #circle(radius: 3pt, fill: accent-color)
        ],
        align(right + horizon)[
          #if date != none [*Issue Date:* #date]
        ]
      )
    ]
    
    #v(2em)
  ]

  // ===== MAGAZINE HEADINGS =====
  show heading.where(level: 1): it => [
    #v(2em)
    #block[
      // Article number
      #rect(
        width: 2em,
        height: 2em,
        fill: primary-color,
        radius: 100%,
        inset: 0pt
      )[
        #align(center + horizon)[
          #text(
            size: 14pt,
            weight: "bold",
            fill: white
          )[#counter(heading).display()]
        ]
      ]
      
      #v(-1.5em)
      #h(3em)
      
      // Article title
      #text(
        size: 22pt,
        weight: "bold",
        fill: primary-color,
        font: ("Arial", "sans-serif")
      )[#it.body]
      
      #v(0.5em)
      #line(length: 80%, stroke: 2pt + accent-color)
    ]
    #v(1.2em)
  ]

  show heading.where(level: 2): it => [
    #v(1.5em)
    #rect(
      fill: secondary-color.lighten(90%),
      stroke: (left: 4pt + secondary-color),
      inset: (left: 1em, rest: 0.8em),
      width: 100%
    )[
      #text(
        size: 16pt,
        weight: "bold",
        fill: secondary-color,
        font: ("Arial", "sans-serif")
      )[#it.body]
    ]
    #v(1em)
  ]

  show heading.where(level: 3): it => [
    #v(1em)
    #text(
      size: 13pt,
      weight: "bold",
      fill: accent-color,
      font: ("Arial", "sans-serif")
    )[
      ■ #it.body
    ]
    #v(0.6em)
  ]

  // ===== DROP CAP EFFECT =====
  show par: it => {
    if it.children.len() > 0 and type(it.children.first()) == "text" {
      let first-char = str(it.children.first()).first()
      if first-char != none and first-char.len() > 0 {
        // Only apply to paragraphs that start a new section/article
        context {
          let is-new-section = query(selector(heading).before(here())).len() > 0 and 
                              query(selector(par).before(here())).len() == 0
          
          if is-new-section and first-char.match(regex("[A-Za-z]")) != none {
            // Drop cap style
            box(
              width: 3em,
              height: 3em,
              inset: (right: 0.5em)
            )[
              #align(center + bottom)[
                #text(
                  size: 48pt,
                  weight: "bold",
                  fill: primary-color,
                  font: ("Times New Roman", "serif")
                )[#first-char]
              ]
            ]
            
            // Rest of the text
            box(
              width: calc.min(100% - 3.5em, 100%),
              inset: (top: 0.5em)
            )[
              #let rest-text = str(it.children.first()).slice(1)
              #text(size: 10.5pt)[#rest-text]
              // Add remaining children if any
              #for child in it.children.slice(1) [ #child ]
            ]
          } else {
            it
          }
        }
      } else {
        it
      }
    } else {
      it
    }
  }

  // ===== PULL QUOTES =====
  show quote: it => [
    #v(1.5em)
    #grid(
      columns: (1fr, 4fr, 1fr),
      gutter: 1em,
      [],
      rect(
        fill: accent-color.lighten(95%),
        stroke: (
          left: 4pt + accent-color,
          right: 4pt + accent-color
        ),
        inset: (x: 1.5em, y: 1em),
        radius: (left: 8pt, right: 8pt)
      )[
        #set text(
          size: 13pt,
          style: "italic",
          fill: accent-color.darken(20%),
          font: ("Georgia", "serif")
        )
        #set par(leading: 0.8em, first-line-indent: 0pt)
        #align(center)[#it.body]
      ],
      []
    )
    #v(1em)
  ]

  // ===== CODE BLOCKS =====
  show raw.where(block: true): it => [
    #v(1em)
    #rect(
      width: 100%,
      fill: light-bg,
      stroke: 1pt + border-color,
      radius: 4pt,
      inset: 1em
    )[
      #set text(
        font: ("Courier New", "monospace"),
        size: 9pt,
        fill: text-color
      )
      #it
    ]
    #v(0.5em)
  ]

  // ===== INLINE CODE =====
  show raw.where(block: false): it => [
    #box(
      fill: light-bg,
      stroke: 0.5pt + border-color,
      outset: (x: 3pt, y: 1pt),
      radius: 2pt
    )[
      #text(
        font: ("Courier New", "monospace"),
        size: 0.9em,
        fill: text-color
      )[#it]
    ]
  ]

  // ===== MAGAZINE LISTS =====
  show list: it => [
    #v(0.5em)
    #set list(marker: text(fill: primary-color)[▪])
    #it
    #v(0.3em)
  ]

  show enum: it => [
    #v(0.5em)
    #set enum(numbering: n => rect(
      width: 1.5em,
      height: 1.5em,
      fill: secondary-color,
      radius: 100%,
      inset: 0pt
    )[
      #align(center + horizon)[
        #text(
          size: 8pt,
          weight: "bold",
          fill: white
        )[#n]
      ]
    ])
    #it
    #v(0.3em)
  ]

  // ===== MAGAZINE TABLES =====
  set table(
    stroke: none,
    fill: (x, y) => {
      if y == 0 { primary-color.lighten(90%) }
      else if calc.odd(y) { light-bg }
      else { white }
    },
    inset: 8pt
  )

  show table: it => [
    #v(1em)
    #rect(
      stroke: 1pt + border-color,
      radius: 6pt,
      inset: 0pt
    )[#it]
    #v(0.5em)
  ]

  // ===== LINKS & EMPHASIS =====
  show link: it => text(fill: secondary-color, decoration: "underline")[#it]
  show strong: it => text(fill: primary-color, weight: "bold")[#it]
  show emph: it => text(fill: accent-color, style: "italic")[#it]

  // ===== MAIN CONTENT =====
  body
}

// Default template call
#show: magazine-template.with(
  title: [MAGAZINE STYLE],
  subtitle: [Professional Publication Layout],
  author: [Editorial Team],
  date: datetime.today().display("[day]. [month repr:long] [year]")
)
