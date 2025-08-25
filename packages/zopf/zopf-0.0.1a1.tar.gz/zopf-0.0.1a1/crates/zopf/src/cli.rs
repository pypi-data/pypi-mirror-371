#[derive(clap::Parser)]
#[command(version, about, long_about = None)]
#[command(propagate_version = true)]
pub struct Cli {
    #[command(subcommand)]
    pub command: Subcommand,
}

#[derive(clap::Subcommand)]
pub enum Subcommand {
    Check,
}

pub fn run(args: Vec<String>) {
    use clap::Parser;

    match Cli::parse_from(args).command {
        Subcommand::Check => {
            println!("Checking...");
        }
    }
}
