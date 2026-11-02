// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;

public class CinderRelay : ModuleRules
{
	public CinderRelay(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "InputCore", "EnhancedInput", "UMG", "AIModule", "NavigationSystem", "GameplayTasks" });

		PrivateDependencyModuleNames.AddRange(new string[] { "Slate", "SlateCore", "LevelSequence", "MovieScene", "AnimGraphRuntime" });
		// Editor-only Designer migration uses the native widget GUID registration API.
		if (Target.bBuildEditor)
			PrivateDependencyModuleNames.Add("UMGEditor");
		// Read native frame counters only in the opt-in Development acceptance runner.
		if (Target.Configuration != UnrealTargetConfiguration.Shipping)
			PrivateDependencyModuleNames.AddRange(new string[] { "RenderCore", "RHI", "AudioMixer" });

		// Uncomment if you are using Slate UI
		// PrivateDependencyModuleNames.AddRange(new string[] { "Slate", "SlateCore" });

		// Uncomment if you are using online features
		// PrivateDependencyModuleNames.Add("OnlineSubsystem");

		// To include OnlineSubsystemSteam, add it to the plugins section in your uproject file with the Enabled attribute set to true
	}
}
