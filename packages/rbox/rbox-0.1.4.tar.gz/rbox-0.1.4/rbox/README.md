<p align="center">
  <h1 align="center">rbox</h1>
</p>

<p align="center">
  <i>rbox</i> gives you full control over your Rekordbox data.
</p>

<p align="center">
  <a title="GitHub" target="_blank" href="https://github.com/dylanljones/rbox"><img alt="Crates.io" src="https://img.shields.io/badge/github-8da0cb?style=for-the-badge&labelColor=555555&logo=github" style="height:20px;"></a>
  <a title="Rust" target="_blank" href="https://crates.io/crates/rbox"><img alt="Crates.io" src="https://img.shields.io/crates/v/rbox.svg?style=for-the-badge&color=fc8d62&logo=rust" style="height:20px;"></a>
  <a title="Docs" target="_blank" href="https://docs.rs/rbox"><img src="https://img.shields.io/badge/docs.rs-rbox-66c2a5?style=for-the-badge&labelColor=555555&logo=docs.rs" style="height:20px;"></a>
</p>


> **⚠️ Disclaimer**: This project is **not** affiliated with Pioneer DJ, AlphaTheta Corp., or any related entities.
> The maintainers and contributors assume no liability for any data loss or damage to your Rekordbox library.
> "Rekordbox" is a registered trademark of AlphaTheta Corporation.

**rbox** is a high-performance Rust library for seamlessly interacting with Pioneer DJ's Rekordbox software data.
It supports the following Rekordbox files:

- **Rekordbox database**: Query and update the Rekordbox v6/v7 master.db database through a type-safe ORM
- **XML database**: Read and write Rekordbox XML database files
- **Analysis Files**: Read and write ANLZ files containing waveforms, beat grids, hot cues and more
- **Settings Access**: Read and write My-Setting files


## 🔧 Installation

rbox is available on Cargo. Run the following Cargo command in your project directory:
```shell
cargo add rbox
```
or add the following line to your Cargo.toml:
```shell
rbox = "0.1.4"
```


## 🚀 Quick-Start

> **❗ Caution**:
> Please make sure to back up your Rekordbox collection before making changes to rekordbox data.
> The backup dialog can be found under "File" > "Library" > "Backup Library"

### Rekordbox 6/7 database

Rekordbox 6 and 7 use a SQLite database for storing the collection content.
Unfortunatly, the `master.db` SQLite database is encrypted using
[SQLCipher][sqlcipher], which means it can't be used without the encryption key.
However, since your data is stored and used locally, the key must be present on the
machine running Rekordbox.

rbox can unlock the new Rekordbox `master.db` SQLite database and provides
an easy interface for accessing and updating the data stored in it.

```rust
use rbox::prelude::*;

fn main() -> anyhow::Result<()> {
    let mut db = MasterDb::open()?;
    let contents = db.get_content()?;
    for content in contents {
        println!("{:?}", content);
    }
    Ok(())
}
```


### Rekordbox XML

The Rekordbox XML database is used for importing (and exporting) Rekordbox collections
including track metadata and playlists. They can also be used to share playlists
between two databases.

rbox can read and write Rekordbox XML databases.

```rust
use rbox::prelude::*;

fn main() -> anyhow::Result<()> {
    let mut xml = RekordboxXml::load("database.xml");
    let tracks = xml.get_tracks();
    for track in tracks {
        println!("{:?}", track);
    }
    Ok(())
}
```

### Rekordbox ANLZ files

Rekordbox stores analysis information of the tracks in the collection in specific files,
which also get exported to decives used by Pioneer professional DJ equipment. The files
have names like `ANLZ0000` and come with the extensions `.DAT`, `.EXT` or `.2EX`.
They include waveforms, beat grids (information about the precise time at which
each beat occurs), time indices to allow efficient seeking to specific positions
inside variable bit-rate audio streams, and lists of memory cues and loop points.

rbox can parse and write all three analysis files.

```rust
use rbox::prelude::*;

fn main() -> anyhow::Result<()> {
    let mut anlz = Anlz::load("ANLZ0000.DAT")?;
    let grid = anlz.get_beat_grid().unwrap();
    for beat in grid {
        println!("Beat: {} Tempo: {} Time: {}", beat.beat_number, beat.tempo, beat.time);
    }
    Ok(())
}
```


### Rekordbox My-Settings

Rekordbox stores the user settings in `*SETTING.DAT` files, which get exported to USB
devices. These files are either in the `PIONEER`directory of a USB drive
(device exports), but are also present for on local installations of Rekordbox 6.
The setting files store the settings found on the "DJ System" > "My Settings" page of
the Rekordbox preferences. These include language, LCD brightness, tempo fader range,
crossfader curve and other settings for Pioneer professional DJ equipment.

rbox supports both parsing and writing of My-Setting files.

```rust
use rbox::prelude::*;
use rbox::settings::Quantize;

fn main() -> anyhow::Result<()> {
    let mut sett = Setting::load("MYSETTING.DAT")?;
    println!("Quantize: {}", sett.get_quantize()?);
    sett.set_quantize(Quantize::Off)?;
    sett.dump()?;
    Ok(())
}
```


## License

Licensed under either of [Apache License, Version 2.0][LICENSE-APACHE] or [MIT license][LICENSE-MIT] at your option.

Unless you explicitly state otherwise, any contribution intentionally submitted
for inclusion in this crate by you, as defined in the Apache-2.0 license, shall
be dual licensed as above, without any additional terms or conditions.


## Sponsor

If rbox has helped you or saved you time, consider supporting its development - every coffee makes a difference!

[![BuyMeACoffee](https://raw.githubusercontent.com/pachadotdev/buymeacoffee-badges/main/bmc-white.svg)](https://www.buymeacoffee.com/dylanljones)

[sqlcipher]: https://www.zetetic.net/sqlcipher/open-source/
[LICENSE-MIT]: https://github.com/dylanljones/rbox/blob/main/LICENSE-MIT
[LICENSE-APACHE]: https://github.com/dylanljones/rbox/blob/main/LICENSE-APACHE
