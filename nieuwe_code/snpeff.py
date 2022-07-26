import subprocess

with open("files/PGPC_0006.chr21.snpEff.vcf", "w") as cmd_out_file:
    completed_process = subprocess.run(
        # [
        #     "snpeff", "GRCh37.75", "-no-downstream", "-no-intergenic",
        #     "-no-intron", "-no-upstream", "-no-utr", "-noStats",
        #     r"C:\Users\femke\PycharmProjects\pythonProject1\files\PGPC_0006_S1.flt.vcf21",
        # ],
        # stdout=cmd_out_file
        [
            "conda", "run", "snpEff", "-Xmx8g", "GRCh37.75", "-no-downstream", "-no-intergenic",
            "-no-intron", "-no-upstream", "-no-utr", "-verbose", "-noStats",
            "files/PGPC_0006_S1.flt.vcf21",
        ],
        stdout=cmd_out_file
    )
    
