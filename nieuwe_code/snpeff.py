import subprocess, re

def snpeff(output_files, bestanden_lijst):
    for bestand in bestanden_lijst:
        nummer = re.findall(r"00..", bestand)
        with open(bestand, "w") as cmd_out_file:
            completed_process = subprocess.run(
                [
                    "conda", "run", "snpEff", "-Xmx8g", "GRCh37.75", "-no-downstream", "-no-intergenic",
                    "-no-intron", "-no-upstream", "-no-utr", "-verbose", "-noStats",
                    "files/PGPC_" + "".join(nummer) + "_S1.flt.vcf21",
                ],
                stdout=cmd_out_file
            )

def main():
    output_files = ["files/PGPC_0006.chr21.snpEff.vcf", "files/PGPC_0052.chr21.snpEff.vcf"]
    bestanden_lijst = ["files/PGPC_0006_S1.flt.vcf21", "files/PGPC_00052_S1.flt.vcf21"]
    snpeff(output_files, bestanden_lijst)
main()
